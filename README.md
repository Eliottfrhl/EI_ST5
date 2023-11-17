# EI_ST5

## Utilisation

L'utilisation de notre programme se fait simplement en modifiant le path vers le fichier .xml que vous souhaitez analyser en fin de fichier puis en exécutant le fichier.

## Description

L’objectif est de rédiger un script Python capable d’identifier les cycles Zeno au sein d’un système UPPAAL. Pour cela, le programme a comme entrée un fichier .xml issu du logiciel UPPAAL et comme sortie les cycles Zeno du système s’ils existent.
	
Afin de vérifier cette caractéristique d’un cycle, nous avons à notre disposition un algorithme qui se décompose en plusieurs étapes : 

- Identifier les cycles de nos différents Templates. Cela consiste en une simple énumération de cycles dans un graphe orienté, à une légère différence près.
- Extraire les cycles vérifiant la condition suffisante. En s’intéressant aux gardes et aux réinitialisations d’horloge le long de notre cycle, nous pouvons identifier une partie des cycles non-zeno. Cela est possible par la condition suffisante établie au préalable qui nous indique que la présence sur un cycle d’une horloge ayant une réinitialisation à 0 ainsi qu’une garde inférieure supérieure à 0 (x>=k, k!=0) nous assure que le cycle en question est non-zeno.
- Vérifier la condition de synchronisation sur les cycles restants. Enfin nous savons qu’un cycle dépendant par synchronisation de signaux d’un cycle non-zeno sera lui aussi non-zeno.

Tout d’abord, nous devons pouvoir manipuler notre fichier xml. Pour cela, nous utilisons la librairie xml de Python et plus particulièrement ElementTree qui nous permet de considérer notre fichier xml non pas comme une longue chaîne de caractères mais comme un “Arbre à élément”, avec une hiérarchie et des fonctionnalités de recherche d’élément déjà implémentées. Nous utilisons cette librairie initialement dans la fonction main mais également dans d’autres fonctions car nous allons chercher des éléments tout au long de notre code.

Ensuite vient la première étape de notre algorithme : la recherche de cycle. Pour cela, nous utilisons une librairie Python, Networkx, qui permet de créer un Objet Graph pour ensuite en retirer des informations à l’aide d’algorithmes déjà implémentés. Ici nous définissons un Graph par Template de notre système dans la fonction parse_template. Après cela, la fonction find_cycles utilise la fonctionnalité simple_cycles  de la librairie Networkx pour identifier les cycles de notre Template. Malheureusement, les fonctions de détections de cycle au sein d’un graphe ne prennent pas en compte ce que nous appelons les transitions parallèles. Ce sont des transitions ayant des états de départ et d’arrivée similaires mais ayant des caractéristiques (gardes, synchronisation..) différentes. C’est pourquoi nous ajoutons une fonction parallels qui ajoute à notre liste de cycles de nouveaux cycles ayant des transitions parallèles à ceux déjà identifiés.

Maintenant que nous connaissons les cycles de notre système, nous pouvons identifier ceux vérifiant la condition suffisante de non-zenoness grâce à la fonction suffCond. Afin de stocker l’information de la validation ou non de cette condition, nous définissons pour chaque cycle identifié un dictionnaire dont les clés sont le nom des horloges présentes sur notre cycle et dont les valeurs sont 2 booléens : le premier qui vaut True si cette horloge est réinitialisée sur le cycle, False sinon et le deuxième qui vaut True si l’horloge contient une garde inférieure d’une valeur strictement supérieure à 0, False sinon. Pour ce faire, il est nécessaire de bien réussir à récupérer le nom des horloges impliquées. Cette partie est faite par la fonction get_clock_names. Enfin, en extrayant de la liste initiale de cycles, ceux ayant une valeur [True, True] dans leur dictionnaire, nous avons une première liste de cycles non-zeno.

Finalement, nous nous intéressons aux cycles potentiellement zeno restants en vérifiant la condition de synchronisation de non-zenoness. Pour cela, nous itérons à travers tous les cycles potentiellement zeno et toutes leurs transitions dans la fonction syncCond. Si elle se synchronise avec l’envoi d’un signal (caractérisée par un point d’interrogation), nous cherchons la ou les transitions qui envoient ce signal dans les cycles déjà certifiés non-zeno. Si le programme en trouve une alors ce cycle est non-zeno et est ajouté à la liste des cycles non-zeno sur lesquels on cherche les transitions émettrices de signal.

Enfin la fonction reverse prend en entrée tous les cycles trouvés et tous les cycles non-zeno identifiés pour retourner la liste des cycles à priori zeno.

## Tests

Notre programme a été testé sur deux différents systèmes UPPAAL qui servent d’exemples à la plateforme : 
- fischer, pour lequel notre programme trouve un cycle zeno correspondant à (req -> wait -> req)
- train-gate, pour lequel notre programme ne trouve aucun cycle zeno.

## Défauts et corrections futures

Malgré tout, notre programme est encore incomplet sur différents points : 
- Notre fonction de recherche de transition parallèles ne peut détecter au maximum qu’une transition parallèle ; il pourrait y en avoir davantage. L’amélioration est simple à implémenter.
- Le résultat de notre fonction syncCond dépend de l’ordre des cycles potentiellement zeno fournis en entrée. Par exemple, imaginons que le premier cycle potentiellement zeno soit synchronisé sur le deuxième qui lui-même est synchronisé sur un cycle certifié non-zeno. Et bien dans ce cas, notre fonction certifiera non-zeno le deuxième cycle mais pas le premier car au moment de la vérification, celui dont il dépend n’est pas encore dans la liste des cycles certifiés non-zeno. Pour pallier ce problème, une solution serait de créer un graphe orienté qui symboliserait les relations entre différents cycles, où une flèche d’un cycle A à un cycle B symboliserait que le cycle A se synchronise sur le cycle B. De cette manière, en partant des locations bloquantes du graphe puis en remontant, on évite ce problème.
