import base64
import os
import requests

def main():
    # receive the deck folder path
    deckFolder = input('Enter the deck folder path: ')
    print("Deck from main: ", deckFolder)
    createDeckFromFolder(deckFolder)
    
    
def addNoteWithImage(deckName, imagePath):
    with open(imagePath, 'rb') as image:
        imageData = base64.b64encode(image.read()).decode('utf-8')
    response = requests.post('http://localhost:8765', json={
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deckName,
                "modelName": "Basic",
                "fields": {
                    "Front": "",
                    "Back": ""
                },
                "tags": ['image-note'],
                "options": {
                    "allowDuplicate": False
                },
                "picture": {
                    "data": imageData,
                    "filename": os.path.basename(imagePath),
                    "fields": ["Front"]
                }
            }
        }
    })
    if response.status_code != 200:
        print('Error: failed to add note')
        return
    print(f"Added image '{imagePath}' to deck '{deckName}'")
    
def deckExists(deckName):
    # Get all deck names from Anki
    response = requests.post("http://localhost:8765", json={
        "action": "deckNames",
        "version": 6
    })
    allDecks = response.json().get("result", [])
    return deckName in allDecks

def createDeck(deckName):
    # Check if the deck exists before creating it
    if not deckExists(deckName):
        print(f"Creating deck: {deckName}")
        requests.post("http://localhost:8765", json={
            "action": "createDeck",
            "version": 6,
            "params": {
                "deck": deckName
            }
        })
        print(f"Created deck: {deckName}")
    else:
        print(f"Deck '{deckName}' already exists.")
        
def createDeckFromFolder(deckFolder: str):
    folders = deckFolder.split(os.sep)
    folderBeforeDeck = os.sep.join(folders[0:len(folders) - 1])
    for root, dirs, files in os.walk(deckFolder):
        # needs to be fixed
        deckPath = root.replace(folderBeforeDeck, "").strip(os.sep).replace(os.sep, "::")
        if deckPath:
            createDeck(deckPath)
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_path = os.path.join(root, file)
                addNoteWithImage(deckPath, image_path)
    print("Done adding images.")

if __name__ == "__main__":
    main()