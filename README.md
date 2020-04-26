# detecNote
Cours de traitement d'image

He-Arc 2020

François Bouthillier de Beaumont - Roxane Carraux - Loïc Jurasz

Programme utilisant OpenCV et développé en langage python permettant de détecter des notes dans une partition de musique

Le programme pour faire les partitions est MuseScore3.

Il y a une variable tout en haut "show_image" qu'on peut mettre à "False" pour ne pas afficher les images.

L'idée première était de détécter les notes grâce à HoughCircle. Cependant, le fait que les notes soient entre les lignes et aient des formes ovales rendait cette détéction impossible.
On a donc choisi de détecter les lignes horizontales et verticales. Le problème que cela crée est qu'il y a des lignes horizontales et verticales dans le titre de la partition. Pour parer à cela, on prends uniquement des suffisament longues lignes.
On doit ensuite prendre également les petites lignes. Pour les petites lignes horizontales, il s'agit de prendre les lignes qui sont juste au-dessus ou juste en-dessous des 5 lignes de la partition. Pour les lignes verticales, il s'agit des lignes étant collé aux notes noires et blanches (et croches). On vérifie que les petites lignes que l'on prend soit proches des lignes de la partition pour ne pas prendre les lignes du titre.


Nous trions ensuite les grandes lignes de bas en haut et de droite à gauche afin de pouvoir définir le cadre ou les notes seront détéctées. Il faut également rajouter une ligne verticale pour ne pas prendre en compte les clés de sols et clés de fa.

On efface ensuite les lignes pour qu'on ait plus que les notes.

Nous détectons ensuite les contours entre les limites définies. Une fois que nous avons toutes nos notes dans notre liste de contours, on peut les trier de gauche à droite pour les avoir dans l'ordre de lecture.

Nous vérifions ensuite où se situe la note par rapport à nos lignes horizontales.

Nous n'utilisons pas les petites lignes verticales actuellement, elles peuvent être utilisées afin de déterminer si la note est une ronde ou une blanche/noire