import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024

clienti_conectati = {}
lista_mesaje = {}
id_curent = 1


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam lista_mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server."
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == 'DISCONNECT':
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat cu succes. La revedere!"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda in ['PUBLISH', 'DELETE', 'LIST']:
            if adresa_client not in clienti_conectati:
                raspuns = f"EROARE: Trebuie sa fii conectat pentru a folosi comanda {comanda}."
            else:
                if comanda == 'PUBLISH':
                    if not argumente.strip():
                        raspuns = "EROARE: Mesajul nu poate fi gol."
                    else:
                        lista_mesaje[id_curent] = {'text': argumente.strip(), 'autor': adresa_client}
                        raspuns = f"OK: Mesaj publicat cu ID={id_curent}"
                        id_curent += 1

                elif comanda == 'DELETE':
                    if not argumente.strip().isdigit():
                        raspuns = "EROARE: ID-ul introdus trebuie sa fie un numar intreg."
                    else:
                        id_sters = int(argumente.strip())
                        if id_sters not in lista_mesaje:
                            raspuns = f"EROARE: Mesajul cu ID={id_sters} nu a fost gasit."
                        elif lista_mesaje[id_sters]['autor'] != adresa_client:
                            raspuns = "EROARE: Nu esti autorul acestui mesaj."
                        else:
                            del lista_mesaje[id_sters]
                            raspuns = f"OK: Mesajul cu ID={id_sters} a fost sters."

                elif comanda == 'LIST':
                    if not lista_mesaje:
                        raspuns = "OK: Nu exista lista_mesaje publicate pe server."
                    else:
                        raspuns_lista = ["Lista lista_mesaje:"]
                        for m_id, info in lista_mesaje.items():
                            raspuns_lista.append(f"  [ID: {m_id}] {info['text']}")
                        raspuns = "\n".join(raspuns_lista)
        elif comanda == 'LIST':
            raspuns = "EROARE: Comanda LIST nu este inca implementata."

        else:
            raspuns = f"EROARE: Comanda '{comanda}' este necunoscuta. Comenzi valide: CONNECT, DISCONNECT, PUBLISH, DELETE, LIST"

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")