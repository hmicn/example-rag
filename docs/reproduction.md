# Procédure de reproduction

## 1. Cloner le dépôt

```bash
git clone https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10.git
cd equipe10
```

## 2. Utiliser la branche V2

```bash
git checkout feature/taste-fragrance-rag
```

Ou :

```bash
git switch feature/taste-fragrance-rag
```

## 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

Installer les dépendances complémentaires si nécessaire :

```bash
python -m pip install fastapi uvicorn chromadb ollama pandas requests
```

## 4. Vérifier la syntaxe du code

```bash
python -m py_compile api.py
python -m py_compile config.py
python -m py_compile ingest.py
python -m py_compile rag.py
```

## 5. Vérifier les données

Afficher les fichiers disponibles :

```bash
find data -maxdepth 2 -type f -print
```

Vérifier le fichier de connaissances :

```bash
python -c "import pandas as pd; df = pd.read_csv('data/taste_fragrance_knowledge_base.csv'); print('Nombre de documents :', len(df))"
```

## 6. Vérifier le jeu de référence

Afficher les fichiers d'évaluation :

```bash
find evaluation -maxdepth 2 -type f -print
```

Vérifier le nombre de cas :

```bash
python -c "import pandas as pd; df = pd.read_csv('evaluation/reference_cases.csv'); print('Nombre de cas :', len(df))"
```

Le protocole final doit être appliqué sur **30 cas de référence**.

## 7. Démarrer le modèle local

Si Ollama est utilisé dans l'environnement :

```bash
ollama serve
```

Dans un autre terminal, télécharger les modèles nécessaires :

```bash
ollama pull qwen3-embedding:4b
ollama pull qwen2.5:1.5b
```

> Les noms exacts des modèles doivent être vérifiés dans `config.py`.

## 8. Vérifier la configuration

```bash
cat config.py
```

Vérifier notamment :

- le modèle d'embeddings ;
- le modèle de génération ;
- le nom de la collection ChromaDB ;
- le chemin des données ;
- le chemin de la base vectorielle.

## 9. Indexer les documents

```bash
python ingest.py
```

Cette commande prépare la collection vectorielle utilisée par le système RAG.

## 10. Démarrer l'API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Ou :

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## 11. Tester le health check

Dans un autre terminal :

```bash
curl http://127.0.0.1:8000/health
```

## 12. Ouvrir Swagger

Documentation Swagger locale :

```text
http://127.0.0.1:8000/docs
```

Spécification OpenAPI :

```text
http://127.0.0.1:8000/openapi.json
```

## 13. Tester la recherche documentaire

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Je cherche un parfum floral au jasmin.",
    "top_k": 4
  }'
```

## 14. Tester une réponse RAG

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Je cherche un parfum floral et élégant au jasmin.",
    "top_k": 4
  }'
```

## 15. Tester avec Swagger

Dans Swagger :

1. ouvrir `/docs` ;
2. sélectionner `POST /search` ou `POST /ask` ;
3. cliquer sur `Try it out` ;
4. saisir la requête JSON ;
5. cliquer sur `Execute` ;
6. vérifier la réponse ;
7. vérifier les sources retournées.

## 16. Exposer l'API

Après le démarrage de l'API, exposer le port `8000` avec l'outil disponible dans l'environnement.

L'URL publique devra ensuite être ajoutée dans :

```text
docs/links.md
```

## 17. Vérification finale

Vérifier les éléments suivants :

- [ ] Branche active : `feature/taste-fragrance-rag`
- [ ] Données présentes
- [ ] Configuration valide
- [ ] Documents indexés
- [ ] API démarrée
- [ ] Endpoint `/health` fonctionnel
- [ ] Endpoint `/search` fonctionnel
- [ ] Endpoint `/ask` fonctionnel
- [ ] Swagger accessible
- [ ] OpenAPI accessible
- [ ] Liens documentés
- [ ] Résultats sauvegardés

## 18. Reproductibilité

La procédure doit permettre à un autre membre de l'équipe de :

1. cloner le dépôt ;
2. sélectionner la branche V2 ;
3. installer les dépendances ;
4. préparer la base vectorielle ;
5. démarrer l'API ;
6. tester les endpoints ;
7. reproduire le résultat présenté lors de la démonstration.
