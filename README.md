# JARVIS Mobile Access

Cette version comprend l'application compagnon iOS et un pont Windows pour démarrer le serveur Flask JARVIS à la demande.

## Configuration Windows (à faire une seule fois)

1. Télécharge les fichiers windows/JARVIS_Mobile_Bridge.py et windows/JARVIS_Setup_Mobile_Bridge.ps1 depuis le dépôt et place-les dans le même dossier.
2. Vérifie que Python est installé et que python.exe fonctionne dans PowerShell.
3. Ouvre PowerShell dans ce dossier et lance :
   powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\JARVIS_Setup_Mobile_Bridge.ps1
4. Copie la clé privée affichée par le script et garde-la secrète. Elle est aussi enregistrée localement dans %LOCALAPPDATA%\JARVIS\mobile-bridge.json.
5. Le script installe une tâche à l'ouverture de session Windows et lance le pont sur 127.0.0.1:8765.

Le pont démarre actions.py si http://127.0.0.1:5000/ping ne répond pas, puis relaie les requêtes vers Flask.

## Tunnel Cloudflare

Le tunnel doit pointer vers le pont, et non directement vers Flask :

   powershell
   cloudflared tunnel --url http://127.0.0.1:8765

Entre l'URL HTTPS https://....trycloudflare.com affichée dans l'application et la clé privée ci-dessus. Tant que le processus Quick Tunnel reste lancé, cette URL peut être utilisée même si Flask s'arrête puis redémarre. Si le tunnel est arrêté ou recréé, son URL temporaire change : il faudra la mettre à jour dans l'application. Pour un accès permanent après redémarrage, configure un tunnel Cloudflare nommé avec un domaine stable.

## Construire l'application iOS

1. Ouvre l'onglet Actions : https://github.com/Arthe1200/jarvis-mobile-access/actions
2. Lance Build JARVIS iOS app sur la branche main.
3. Télécharge l'artifact JARVIS-unsigned-IPA.
4. L'IPA n'est pas signé : signe-le avec ton identifiant Apple via un outil de sideloading avant de l'installer.

## Limites honnêtes

- Le pont démarre uniquement le serveur Flask sur un PC déjà allumé et connecté à sa session Windows. Il ne réveille pas un PC éteint.
- Le tunnel doit être déjà lancé et rester accessible. Un Quick Tunnel ne permet pas de retrouver automatiquement sa nouvelle URL après un redémarrage.
- La clé autorise le démarrage de Flask ; ne la partage pas. Le pont n'expose que l'adresse locale 127.0.0.1 et ne doit être utilisé qu'avec un tunnel de confiance.
- Les raccourcis Assistant/Voix/PC ouvrent l'interface existante /mobile. La caméra et les fonctions natives ne sont pas encore implémentées par ce pont.
