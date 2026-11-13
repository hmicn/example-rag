# Protocole d'évaluation V2

## 1. Objectif

L'objectif est de mesurer la qualité du système RAG sur des cas représentatifs de son application.

Les cas doivent représenter les besoins réels des utilisateurs dans les domaines :

- Fragrance & Beauty ;
- Taste & Wellbeing ;
- Shared.

L'évaluation ne doit pas mesurer uniquement la fluidité des réponses. Elle doit également vérifier :

- leur exactitude ;
- leur pertinence ;
- leur conformité aux sources ;
- leur robustesse ;
- leur performance ;
- leur sécurité.

## 2. Jeu de référence

Fichier utilisé :

```text
evaluation/reference_cases.csv
```

Nombre attendu :

```text
30 cas de référence
```

Les cas peuvent inclure :

1. des questions simples ;
2. des demandes de recommandation ;
3. des recherches de produits ;
4. des questions ambiguës ;
5. des questions nécessitant plusieurs documents ;
6. des questions sans réponse disponible ;
7. des formulations alternatives ;
8. des situations présentant un risque d'hallucination.

## 3. Dimensions évaluées

Les principales dimensions d'évaluation sont l'exactitude, la pertinence, la factualité, le raisonnement, la robustesse, la sécurité et la performance.

### 3.1 Exactitude

La réponse est-elle correcte par rapport aux documents de référence ?

### 3.2 Pertinence

La réponse répond-elle réellement à la demande de l'utilisateur ?

### 3.3 Factualité

La réponse contient-elle des informations non présentes dans les sources ?

### 3.4 Exhaustivité

Les informations importantes attendues sont-elles présentes ?

### 3.5 Robustesse

La réponse reste-t-elle correcte lorsque la question est reformulée ?

### 3.6 Sécurité

Le système évite-t-il :

- les informations inventées ;
- les réponses non justifiées ;
- la divulgation de données sensibles ;
- les réponses inappropriées ?

### 3.7 Performance

Mesurer :

- la latence de recherche ;
- la latence de génération ;
- la latence totale ;
- le nombre de documents récupérés ;
- les distances vectorielles ;
- le coût éventuel du modèle.

## 4. Méthode d'évaluation

Pour chaque cas :

1. lire l'identifiant du cas ;
2. envoyer la question à l'endpoint `/ask` ;
3. enregistrer la réponse générée ;
4. enregistrer les sources utilisées ;
5. enregistrer les distances vectorielles ;
6. mesurer la latence ;
7. vérifier les mots-clés attendus ;
8. comparer la réponse avec la référence ;
9. relever les erreurs éventuelles ;
10. sauvegarder le résultat.

## 5. Format des résultats

Les résultats peuvent être enregistrés dans :

```text
results/evaluation_v2.csv
```

Colonnes proposées :

```text
case_id
domain
question
reference_answer
generated_answer
sources
latency_ms
keyword_match
factuality
relevance
completeness
notes
```

## 6. Grille de notation

Chaque critère peut être noté de 0 à 5.

| Note | Interprétation |
|---|---|
| 0 | Absence de réponse ou réponse incorrecte |
| 1 | Réponse très insuffisante |
| 2 | Réponse partiellement correcte |
| 3 | Réponse globalement correcte |
| 4 | Réponse correcte et pertinente |
| 5 | Réponse correcte, complète, sourcée et adaptée |

## 7. Pondération proposée

| Critère | Poids |
|---|---:|
| Exactitude technique | 40 % |
| Clarté et pertinence | 25 % |
| Exhaustivité | 20 % |
| Respect des consignes | 15 % |
| **Total** | **100 %** |

## 8. Évaluation humaine

Une évaluation humaine peut examiner :

- l'exactitude ;
- la clarté ;
- l'exhaustivité ;
- les sources ;
- le respect des consignes.

L'évaluation humaine permet de tenir compte du contexte métier, mais elle peut être coûteuse et subjective.

## 9. Évaluation sur les cas métier

Le jeu de tests doit représenter :

- les vrais besoins utilisateurs ;
- les cas difficiles ;
- les ambiguïtés ;
- les situations à risque.

Cette méthode permet de vérifier la qualité du modèle dans des conditions proches de son utilisation réelle.

## 10. Test réalisé

### Question

```text
Je cherche un parfum floral et élégant au jasmin.
```

### Sources retrouvées

1. Commander un parfum floral ;
2. Jasmin éclatant ;
3. Rose poudrée ;
4. Introduction.

### Résultat observé

```text
Pour commander un parfum floral élégant au jasmin, vous pouvez choisir
le produit « Velours Floral ».
```

## 11. Comparaison V1/V2

La comparaison doit porter sur :

- le nombre de documents ;
- la structure des données ;
- les domaines couverts ;
- la qualité de la recherche ;
- la pertinence des sources ;
- la qualité des réponses ;
- le taux d'erreurs factuelles ;
- la latence ;
- la robustesse ;
- les limites.

## 12. Fichiers attendus

```text
results/evaluation_v2.csv
results/evaluation_summary.md
```

## 13. Résumé final

Le rapport final doit présenter :

- le nombre de cas testés ;
- le score moyen ;
- les critères utilisés ;
- les erreurs principales ;
- les cas réussis ;
- les limites ;
- les biais éventuels ;
- les améliorations possibles.
