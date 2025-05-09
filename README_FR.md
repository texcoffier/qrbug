# QRBug

[🇬🇧 English](https://github.com/texcoffier/qrbug/blob/main/README.md)

QRBug est un logiciel fait pour permettre à n'importe quel utilisateur de signaler des défaillances ou problèmes sur n'importe quel équipement en utilisant de simples QR Codes.  
Le logiciel a été originellement développé pour l'Université Claude Bernard Lyon 1.

## Installation
Pour commencer, installez Python version 3.10 ou plus *(nous recommandons 3.12)*.  
Clonez ou téléchargez ce repo vers un dossier local.

### Linux
Nous avons préparé un script d'installation pour les utilisateurs Linux : `./install.sh`  
Lancez-le, et vous serez paré à lancer le serveur.

### Windows/macOS
Tout d'abord, assuerez-vous que l'exécutable Python est dans votre PATH.  

Créez un nouvel encironnement virtuel à la racine du dossier.  
Pour faire cela, vérifiez bien que vous avez `pip` d'installé.

Ensuite, lancez la commande `pip install virtualenv` afin de vérifier que vous pouvez créer des environnements virtuels.

Créez l'environnement virtuel avec la commande `python -m venv .venv`.

Activez ce nouvel environnement virtuel :  
Sur **macOS** : `source .venv/bin/activate`  
Sur **Windows** : `.venv\Scripts\activate`

Pour finir, installez le logiciel et tout ses dépendances dans l'environnement virtuel :  
```bash
python -m pip install -e .
```

## Tests
Pour vérifier que tous les tests passent, vous pouvez lancer le script `test.sh` sur Linux, ou la commande `python -m unittest` pour les autres systèmes d'exploitation.

## Lancement
Pour lancer le serveur, utilisez la commande suivante :
```bash
python -m aiohttp.web -H "<IP>" -P "<PORT>" qrbug.server:init_server
```
Bien évidemment, replacez `<IP>` et `<PORT>` avec les valeurs correspondantes.  
Si vous n'êtes pas sûr de quoi y mettre, remplacez `<IP>` par `localhost` et `<PORT>` par `8080`.
