# JARVIS Mobile Access

Ce dépôt contient deux éléments :
- une page d'accès statique publiée avec GitHub Pages ;
- un premier prototype d'application iOS Capacitor, compilé sur un runner macOS de GitHub Actions.

## Page d'accès web

Adresse : https://arthe1200.github.io/jarvis-mobile-access/

La page demande l'adresse HTTPS actuelle du Cloudflare Quick Tunnel et ouvre ensuite `/mobile` sur ce tunnel. Le Quick Tunnel change généralement à chaque redémarrage, donc cette page ne peut pas découvrir automatiquement la nouvelle adresse.

## Construire le prototype iOS

1. Ouvre l'onglet **Actions** du dépôt : https://github.com/Arthe1200/jarvis-mobile-access/actions
2. Sélectionne **Build JARVIS iOS app**.
3. Clique sur **Run workflow**, puis confirme sur la branche `main`.
4. Attends que le workflow soit terminé avec le statut vert.
5. Ouvre l'exécution et télécharge l'artifact **JARVIS-unsigned-IPA**.

Le fichier produit est un IPA **non signé**. Il doit être signé avec ton identifiant Apple avant l'installation, par exemple via un outil de sideloading tel que Sideloadly. Avec un compte Apple gratuit, la signature personnelle est temporaire et doit généralement être renouvelée tous les 7 jours.

## État du prototype

L'écran iOS propose maintenant un tableau de bord sombre, une configuration d'adresse HTTPS enregistrée sur l'iPhone, un test de joignabilité réseau et un accès à `/mobile`.

**Limites actuelles :**
- Le test réseau confirme seulement qu'une réponse arrive ; il ne vérifie pas que l'API JARVIS fonctionne ni que l'accès est authentifié.
- Le tunnel Cloudflare Quick Tunnel n'est pas découvert automatiquement et son adresse peut changer au redémarrage.
- Les raccourcis Assistant, Voix et PC ouvrent l'interface distante `/mobile`. La caméra et les actions natives ne sont pas encore raccordées.
- L'interface complète de `mobile.html` n'est pas embarquée dans l'application.

## Feuille de route technique

1. **Connexion fiable :** ajouter une vraie route de santé côté serveur, avec une réponse JSON minimale et authentification.
2. **Interface :** examiner l'interface actuelle `mobile.html` et décider si elle doit être embarquée dans Capacitor ou servie depuis le PC.
3. **Assistant :** connecter la conversation aux routes existantes du serveur, avec gestion des erreurs et des réponses en cours.
4. **Voix et caméra :** ajouter les permissions iOS et un parcours de test explicite.
5. **Contrôle PC :** exposer uniquement des commandes autorisées, avec confirmation avant toute action sensible.
6. **Sécurité :** éviter les secrets dans le dépôt, protéger l'accès distant et privilégier un tunnel privé/authentifié.

## Sécurité

- Ne committe jamais une adresse active de tunnel, un jeton DuckDNS, un mot de passe, une clé VAPID privée ou toute autre donnée secrète.
- Ne considère pas une adresse de tunnel comme une authentification. Toute personne qui obtient l'adresse peut essayer d'accéder à l'interface exposée.
- Pour une utilisation durable, protège l'accès à JARVIS avec une authentification solide ou une couche d'accès privée avant d'y connecter des fonctions sensibles.
