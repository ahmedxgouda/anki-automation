import base64
import os
import requests
from pdf_to_images import pdf_to_images
import re

def main():
    # receive the deck folder path
    deckFolder = input('Enter the deck folder path: ')
    convertAndAddPdf = input('Do you want to convert PDFs to images and add them to Anki? (y/n): ')
    while convertAndAddPdf.lower() not in ['y', 'n']:
        convertAndAddPdf = input('Please enter y or n: ')
    toConvert = convertAndAddPdf.lower() == 'y'
    createDeckFromFolder(deckFolder, toConvert)
    
    
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
        
def createDeckFromFolder(deckFolder: str, convertPdf: bool):
    folders = deckFolder.split(os.sep)
    folderBeforeDeck = os.sep.join(folders[0:len(folders) - 1])
    
    def sortByNumber(file):
        regex = re.search(r'\d+', file)
        if regex:
            return int(regex.group())
        return 0
    
    for root, dirs, files in os.walk(deckFolder):
        # needs to be fixed
        deckPath = root.replace(folderBeforeDeck, "").strip(os.sep).replace(os.sep, "::")
        if deckPath:
            createDeck(deckPath)
        sortedFiles = sorted(files, key=sortByNumber)
        for file in sortedFiles:
            if file.endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_path = os.path.join(root, file)
                addNoteWithImage(deckPath, image_path)
            elif convertPdf and file.endswith(".pdf"):
                print(f"Adding images from PDF: {file}")
                pdf_path = os.path.join(root, file)
                output_folder = pdf_path.replace('.pdf', '')
                # Create the deck path for the PDF
                pdfDeckPath = deckPath + "::" + file.replace(".pdf", "")
                createDeck(pdfDeckPath)
                pdf_to_images(pdf_path, output_folder)
                images = os.listdir(output_folder)
                # sort by numbers from 1, 2, 3 and so on
                images = sorted(images, key=sortByNumber)
                for image in images:
                    image_path = os.path.join(output_folder, image)
                    addNoteWithImage(pdfDeckPath, image_path)
    print("Done adding images.")
    
if __name__ == "__main__":
    main()
