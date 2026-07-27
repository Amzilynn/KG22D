                Prompt utilisateur
                        │
                        ▼
          ┌────────────────────────┐
          │     Prompt Parser      │
          └────────────────────────┘
                        │
                        ▼
        Extraction des entités et contraintes
                        │
                        ▼
          ┌────────────────────────┐
          │    KG Builder          │
          └────────────────────────┘
                        │
                        ▼
             Knowledge Graph (Neo4j/NetworkX)
                        │
                        ▼
          ┌────────────────────────┐
          │    Rule Engine         │
          └────────────────────────┘
                        │
                        ▼
          KG enrichi et validé
                        │
                        ▼
          ┌────────────────────────┐
          │  Floor Graph Builder   │
          └────────────────────────┘
                        │
                        ▼
            Graphe spatial des pièces
                        │
                        ▼
          ┌────────────────────────┐
          │ Layout Optimizer       │
          └────────────────────────┘
                        │
                        ▼
          Coordonnées des pièces
                        │
                        ▼
          ┌────────────────────────┐
          │     Renderer 2D        │
          └────────────────────────┘
                        │
                        ▼
                 Plan SVG / DXF



                 Exemple avec un prompt
Prompt
Je veux une villa S+2 moderne avec :

- 4 chambres
- une cuisine ouverte
- un salon
- une salle à manger
- un garage
- une piscine
- un bureau
1. prompt_parser.py

Produit un JSON structuré :

{
  "building": "villa",
  "floors": 3,
  "style": "modern",
  "rooms": [
    "living_room",
    "kitchen",
    "office",
    "garage",
    "pool"
  ],
  "bedrooms": 4
}
2. kg_builder.py

Construit le graphe :

Villa
│
├── hasFloor → GroundFloor
├── hasFloor → Floor1
├── hasFloor → Floor2
│
├── hasRoom → LivingRoom
├── hasRoom → Kitchen
├── hasRoom → Garage
├── hasRoom → Office
└── hasRoom → Pool
3. graph_reasoner.py

Ajoute automatiquement des connaissances :

Kitchen
     adjacent_to
LivingRoom

Garage
     near
Entrance

Pool
     outside

Bedrooms
     upstairs

Ces règles peuvent provenir d'une base de connaissances ou d'une ontologie.

4. optimizer.py

Calcule les positions :

┌─────────────────────────────┐
│            Salon            │
├──────────────┬──────────────┤
│ Cuisine      │ Salle à manger
├──────────────┼──────────────┤
│ Bureau       │ Garage
└──────────────┴──────────────┘
5. svg_renderer.py

Produit un plan 2D comme :

+------------------------------------------------+
|                Living Room                     |
+----------------------+-------------------------+
| Kitchen              | Dining Room             |
+----------------------+-------------------------+
| Office               | Garage                  |
+-----------------------------------------------+
Évolution vers ton projet de stage

Comme ton projet inclut aussi la recommandation de matériaux écologiques, tu peux ajouter un module dédié :

AI_Architect/
│
├── recommendation/
│   ├── material_selector.py
│   ├── carbon_analyzer.py
│   ├── thermal_analyzer.py
│   ├── cost_estimator.py
│   ├── vector_store.py
│   ├── rag_engine.py
│   └── report_generator.py

Ainsi, le pipeline devient :

Prompt
   │
   ▼
Knowledge Graph
   │
   ├────────► Génération du plan 2D
   │
   └────────► Analyse des pièces
                │
                ▼
      Recommandation des matériaux
                │
                ▼
      Rapport (coût, carbone, isolation, durabilité)

Cette séparation entre compréhension du besoin, modélisation (KG), génération géométrique et analyse des matériaux est une architecture propre, extensible et adaptée à un projet d'IA pour les architectes.