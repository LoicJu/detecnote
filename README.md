# detecNote

Cours de traitement d'image - Oliver Hüsser

He-Arc 2020

Bouthillier - Roxane Carraux - Loïc Jurasz

## Dépendances

Pour télécharger le repo :

```
git clone https://github.com/LoicJu/detecnote.git
```

Pour installer les bibliothèques nécessaires : 

```
pip install -r requirements.txt
```

## Configuration

Par défaut, le programme va afficher les résultats dans des fenêtres d'images. Si l'utilisateur ne veut pas afficher ces dernières et ne générer que le fichier *txt*, il peut définir la variable [SHOW_IMAGE](Main.py#L17) à *False*.

Il est aussi important de préciser si les images ont un fond transparent. La variable [HAS_TRANSPARENT_BC](Main.py#L18) est par défaut à *True*.

Pour passer à l'exemple suivant, il suffit de tapper 0 sur le clavier numérique.

## Explications

Programme utilisant OpenCV et développé en langage python permettant de détecter des notes dans une partition de musique.

Nous utilisons le programme [MuseScore3](https://musescore.org) pour générer les partitions.

L'idée première était de détecter les notes grâce à *HoughCircle*. Cependant, le fait que les notes soient entre les lignes et aient des formes ovales rendait cette détection impossible.
On a donc choisi de détecter les lignes horizontales et verticales. Le problème que cela crée est qu'il y a des lignes horizontales et verticales dans le titre de la partition. Pour parer à cela, on prend uniquement de suffisamment longues lignes.
On doit ensuite prendre également les petites lignes. Pour les petites lignes horizontales, il s'agit de prendre les lignes qui sont juste au-dessus ou juste en dessous des 5 lignes de la partition. Pour les lignes verticales, il s'agit des lignes étant collées aux notes noires et blanches (et croches). On vérifie que les petites lignes que l'on prend soient proches des lignes de la partition pour ne pas prendre les lignes du titre.

Nous trions ensuite les grandes lignes de bas en haut et de droite à gauche afin de pouvoir définir le cadre ou les notes seront détectées. Il faut également rajouter une ligne verticale pour ne pas prendre en compte les clés de sols et clés de fa.

On efface ensuite les lignes pour qu'on ait plus que les notes.

Nous détectons ensuite les contours entre les limites définies. Une fois que nous avons toutes nos notes dans notre liste de contours, on peut les trier de gauche à droite pour les avoir dans l'ordre de lecture.

Nous vérifions ensuite où se situe la note par rapport à nos lignes horizontales et si une petite ligne verticale en est proche.

Nous écrivons ensuite dans un fichier txt les notes que nous avons repérées. Nous écrivons également avant la note (r) ou (n/b) pour dire si la note est une ronde (r) ou une blanche/noir (n/b)
