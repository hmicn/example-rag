# Liens du projet

## Repository GitHub

[Dépôt principal](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10)

## Branche V2

[feature/taste-fragrance-rag](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/tree/feature/taste-fragrance-rag)

## Fichiers importants

- [README](../README.md)
- [Changelog](../CHANGELOG.md)
- [Contrat API](api.md)
- [Protocole d'évaluation](evaluation.md)
- [Procédure de reproduction](reproduction.md)

## API locale

### Base URL

```text
http://127.0.0.1:8000
```

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI JSON

```text
http://127.0.0.1:8000/openapi.json
```

### Health check

```text
http://127.0.0.1:8000/health
```

## API publique

Les liens publics seront ajoutés lorsque l'API sera réellement exposée.

### Base URL publique

```text
https://URL_PUBLIQUE
```

### Swagger public

```text
https://URL_PUBLIQUE/docs
```

### OpenAPI public

```text
https://URL_PUBLIQUE/openapi.json
```

### Health check public

```text
https://URL_PUBLIQUE/health
```

## Validité du lien public

Le lien public peut être temporaire. Il dépend :

- de la session d'exécution ;
- du serveur FastAPI ;
- de l'environnement utilisé ;
- du tunnel public ;
- de la disponibilité du port utilisé.

## Mise à jour du lien public

Après l'obtention de l'URL publique réelle :

1. remplacer `https://URL_PUBLIQUE` par l'URL obtenue ;
2. vérifier `/docs` ;
3. vérifier `/openapi.json` ;
4. vérifier `/health` ;
5. committer la modification ;
6. pousser la branche GitHub.

## Sécurité

Ne jamais publier dans Git :

- un mot de passe ;
- un token GitHub ;
- un token ngrok ;
- une clé API ;
- un fichier `.env` contenant des secrets.
