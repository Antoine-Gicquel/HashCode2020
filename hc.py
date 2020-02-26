import os
os.chdir("D:\\Informatique\\HashCode 2020")

def linspace(a, b, pas):
    n = round((b-a)/pas)
    return [a + i*(b-a)/n for i in range(n)]

inFile = 'c.txt'

print("On creuse l'entree "+inFile)


# parsing the input
f = open("inputs/" + inFile, 'r')
lines = f.readlines()
f.close()

for i in range(len(lines)):
    lines[i] = lines[i].split(" ")

B, L, D = list(map(int,lines[0]))
S = list(map(int,lines[1])) 


Library = []

for i in range(2, 2 + 2*L, 2) :
    nj, tj, mj = list(map(int,lines[i]))
    books = list(map(int,lines[i+1]))
    tab = [(b, S[b]) for b in books]
    tab.sort(key = lambda x:x[1], reverse = True) # on trie les livres de chaque librairie par score décroissant
    Library.append([nj,tj,mj,tab])



## Main part
def getScoreAndLibOrder(valorisation):
    """
    Input : valorisation : un indicateur de à quel point on va valoriser les librairies qui sign-up vite
    Return : (score, output) where output = [(library1, [booksScanned]), (library2, [booksScanned]), ...] in order
    """
    
    isThisBookScanned = [False for i in range(B)]
    isThisLibSigned = [False for i in range(L)]
    

    libOrder = []
    score = 0
    
    # 1ère partie : solution "simple" par un algorithme glouton
    
    d = 0 # current day
    while d < D:
        bestLib = 0
        bestScore = 0
        
        # on regarde la meilleure library
        for iLib in range(len(Library)):
            scoreLib = 0
            if isThisLibSigned[iLib]: continue # pas besoin de calculer si on a déjà traîté la library
            
            nbJoursActifs = D - d - Library[iLib][1] # nb de jours qu'il restera après le sign-up
            nbBooksScannes = 0
            iBook = 0
            while nbBooksScannes < min(nbJoursActifs*Library[iLib][2], Library[iLib][0]) and iBook < Library[iLib][0]:
                if isThisBookScanned[Library[iLib][3][iBook][0]] == False: # si on a pas déjà prévu de scanner le livre depuis une autre lib
                    scoreLib += Library[iLib][3][iBook][1]
                    nbBooksScannes += 1
                iBook += 1
            if scoreLib > 0: # TODO check here
                scoreLib /= Library[iLib][1]**valorisation
                # scoreLib += nbJoursActifs*valorisation # on valorise les petits temps de sign-up en leur donnant un plus gros bonus
                
            if scoreLib > bestScore:
                bestLib = iLib
                bestScore = scoreLib
        
        # on s'arrête si on ne peut plus scanner de livres
        if bestScore == 0:
            break
        
        # on regarde les livres scannables par bestLib
        booksFromBestLib = []
        nbJoursActifs = D - d - Library[bestLib][1]
        nbBooksScannes = 0
        iBook = 0
        while nbBooksScannes < min(nbJoursActifs*Library[bestLib][2], Library[bestLib][0]) and iBook < Library[bestLib][0]:
            if isThisBookScanned[Library[bestLib][3][iBook][0]] == False: # si on a pas déjà prévu de scanner le livre depuis une autre lib
                b = Library[bestLib][3][iBook][0] # indice du livre qu'on ajoute
                booksFromBestLib.append(b)
                isThisBookScanned[b] = True
                score += S[b]
                nbBooksScannes += 1
            iBook += 1
        
        libOrder.append([bestLib, booksFromBestLib])
        isThisLibSigned[bestLib] = True
        
        d += Library[bestLib][1] # on avance dans le nombre de jours
    
    
    # 2ème partie ! Amélioration de la solution trouvée
    # TODO : ameliorer pour faire des chaines (lib1 (sous-chargée) scanne le livre A, ce qui permet à lib2 de scanner B, ce qui permet à lib3 de scanner C)
    # on réarrange le scanning (quelle lib scanne quoi) pour optimiser un peu +
    # l'idée ici :
    # On regarde les librairies qui finissent plus tôt que la deadline. 
    # On regarde les livres qu'elles ont skip (librairies sous-chargées). 
    # En parallèle on regarde les librairies qui avaient encore des livres à scanner après la deadline (librairies surchargées). 
    # Et on essaie de déléguer : si une librairie sous-chargée dispose d'un livre (appelons-le L) qui est scanné par une librairie surchargée, on décharge la librairie surchargée (elle va donc scanner un autre livre que L au lieu de L) et on fait scanner L par la librairie sous-chargée -> on a remplacé 1 scan par 2 !
    
    libsWhichEndedEarly = []
    libsWhichHadBooksLeftToScan = []
    
    # on passe en revue toutes les librairies pour regarder si elles sont sous-chargées ou surchargées
    d = 0
    for iLib, booksScanned in libOrder:
        d += Library[iLib][1]
        nbBooksScanned = len(booksScanned)
        if nbBooksScanned // Library[iLib][2] + 1 < D - d:
            # la librairie est sous-chargée, on se souvient de quels livres la lib aurait pu scanner
            booksCanScan = []
            i = 0
            iScanned = 0
            while i < len(Library[iLib][3]) and iScanned < len(booksScanned):
                if Library[iLib][3][i][0] == booksScanned[iScanned]:
                    iScanned += 1
                else:
                    booksCanScan.append(Library[iLib][3][i][0])
                i += 1
            if len(booksCanScan) > 0:
                nbBooksCanScan = (D - d)*Library[iLib][2] - nbBooksScanned
                libsWhichEndedEarly.append((iLib, booksCanScan, nbBooksCanScan))
        else:
            # la librairie est surchargée, on garde en tête ce qu'elle a scanné, et combien de livres il lui restait à scanner si elle avait eu + de temps
            iLastScan = -1
            booksLeft = 0
            i = 0
            while i < len(Library[iLib][3]):
                if Library[iLib][3][i][0] == booksScanned[-1]:
                    iLastScan = i
                if iLastScan > 0:
                    if isThisBookScanned[Library[iLib][3][i][0]] == False:
                        booksLeft += 1
                i += 1
            if booksLeft > 0:
                libsWhichHadBooksLeftToScan.append([iLib, booksLeft, booksScanned])
    
    
    booksNotToScan = dict() # booksNotToScan[iLib] = [id1, id2, id3, ...] ordered by score. Pour les libs surchargées, les id des livres qu'elles vont pouvoir skip
    booksToScan = dict() # booksToScan[iLib] = [id1, id2, id3, ...] ordered by score. Pour les libs sous-chargées, les id des livres qu'elles vont devoir scanner
    
    # on remplit les dicts
    for iLib, booksCanScan, nbBooksCanScan in libsWhichEndedEarly:
        booksToScan[iLib] = []
        for b in booksCanScan:
            trouveLivre = False
            i = 0
            while not trouveLivre and i < len(libsWhichHadBooksLeftToScan):
                if libsWhichHadBooksLeftToScan[i][1] > 0 and b in libsWhichHadBooksLeftToScan[i][2]:
                    trouveLivre = True
                    libsWhichHadBooksLeftToScan[i][1] -= 1
                    booksToScan[iLib].append(b)
                    if not (libsWhichHadBooksLeftToScan[i][0] in booksNotToScan.keys()):
                        booksNotToScan[libsWhichHadBooksLeftToScan[i][0]] = []
                    booksNotToScan[libsWhichHadBooksLeftToScan[i][0]].append(b)
                    libsWhichHadBooksLeftToScan[i][2].remove(b) # nécéssaire si une autre librairie sous-chargée avait b en stock
                i += 1
            if len(booksToScan[iLib]) == nbBooksCanScan:
                break
    
    
    # on actualise libOrder
    for i in range(len(libOrder)):
        if libOrder[i][0] in booksNotToScan.keys() and len(booksNotToScan[libOrder[i][0]]) > 0:
            # on traite une librairie surchargée
            iLastScan = 0
            libId = libOrder[i][0]
            for b in booksNotToScan[libId]:
                # ici on va faire l'échange : on ne scanne plus b mais un livre qu'on a pas eu le temps de scanner:
                # on enlève b
                try:
                    libOrder[i][1].remove(b) # a peut-être déjà été enlevé au moment du remplissage des dicts (en vrai c'est sûr, mais je préfère laisser le remove)
                except:
                    pass
                score -= S[b]
                
                # on scan un nouveau livre
                while isThisBookScanned[Library[libId][3][iLastScan][0]]: # on cherche l'indice du prochain livre qu'on pourra scanner
                    iLastScan += 1
                libOrder[i][1].append(Library[libId][3][iLastScan][0])
                isThisBookScanned[Library[libId][3][iLastScan][0]] = True
                score += S[Library[libId][3][iLastScan][0]]
                
        elif libOrder[i][0] in booksToScan.keys():
            # on traite une librairie sous-chargée
            for b in booksToScan[libOrder[i][0]]:
                libOrder[i][1].append(b)
                score += S[b]
    
    
    
    # 3ème partie : optimisation de ce que l'on scanne comme livre
    # ici on va échanger des paires (bonLivrePasScanne, mauvaisLivreScanne)
    bookOrderedByScore = list(range(B))
    bookOrderedByScore.sort(key=lambda x:S[x], reverse=True)
    
    dictBooksScannedByLibs = {x:y for x,y in libOrder}
    dictWhoScansThatBook = dict()
    dictWhoHasThatBook = dict()
    for iLib, booksScanned in libOrder:
        for x in booksScanned:
            dictWhoScansThatBook[x] = iLib
    for iLib in range(L):
        for b, bScore in Library[iLib][3]:
            if not b in dictWhoHasThatBook.keys():
                dictWhoHasThatBook[b] = set()
            dictWhoHasThatBook[b].add(iLib)

    
    iWorstBookScanned = B-1
    iBestBookNotScanned = 0
    for i in range(B):
        if not isThisBookScanned[bookOrderedByScore[i]] and bookOrderedByScore[i] in dictWhoHasThatBook.keys():
            iBestBookNotScanned = i
            break
    for i in range(1, B+1):
        if isThisBookScanned[bookOrderedByScore[-i]]:
            iWorstBookScanned = B - i
            break
    
    while iBestBookNotScanned < iWorstBookScanned:
        echangeThisRound = False
        # on essaie d'inverser les deux
        badLib = dictWhoScansThatBook[bookOrderedByScore[iWorstBookScanned]]
        booksSkippedByBadLib = [x[0] for x in Library[badLib][3] if (isThisBookScanned[x[0]] and dictWhoScansThatBook[x[0]] != badLib)]
        goodLibs = [x for x in dictWhoHasThatBook[bookOrderedByScore[iBestBookNotScanned]] if x in dictBooksScannedByLibs.keys()]
        goodLibsBooks = dict()
        for l in goodLibs:
            for b in dictBooksScannedByLibs[l]:
                goodLibsBooks[b] = l
        
        for skippedBook in booksSkippedByBadLib:
            if skippedBook in goodLibsBooks.keys():
                # on fait l'échange
                echangeThisRound = True
                goodLib = goodLibsBooks[skippedBook]
                
                # badLib doit maintenant scanner skippedBook et ne plus scanner bookOrderedByScore[iWorstBookScanned]
                # on cherche l'indice dans libOrder qui correspond à badLib
                badLibInLibOrder = -1
                i = 0
                while i < len(libOrder):
                    if libOrder[i][0] == badLib:
                        badLibInLibOrder = i
                        break
                    i+=1
                libOrder[badLibInLibOrder][1][libOrder[badLibInLibOrder][1].index(bookOrderedByScore[iWorstBookScanned])] = skippedBook
                
                # goodlib doit scanner bookOrderedByScore[iBestBookNotScanned] et ne plus scanner skippedBook
                # on cherche l'indice dans libOrder qui correspond à goodLib
                goodLibInLibOrder = -1
                i = 0
                while i < len(libOrder):
                    if libOrder[i][0] == goodLib:
                        goodLibInLibOrder = i
                        break
                    i+=1
                libOrder[goodLibInLibOrder][1][libOrder[goodLibInLibOrder][1].index(skippedBook)] = bookOrderedByScore[iBestBookNotScanned]
                
                # on met à jour isThisBookScanned et le score
                isThisBookScanned[bookOrderedByScore[iWorstBookScanned]] = False
                isThisBookScanned[bookOrderedByScore[iBestBookNotScanned]] = True
                score += S[bookOrderedByScore[iBestBookNotScanned]] - S[bookOrderedByScore[iWorstBookScanned]]
                
                # recalcul du worst/best en cas d'échange
                for i in range(iBestBookNotScanned + 1, B):
                    if not isThisBookScanned[bookOrderedByScore[i]] and bookOrderedByScore[i] in dictWhoHasThatBook.keys():
                        iBestBookNotScanned = i
                        break
                for i in range((B-iWorstBookScanned) + 1, B+1):
                    if isThisBookScanned[bookOrderedByScore[-i]]:
                        iWorstBookScanned = B - i
                        break
                break
        
        
        # recalcul du worst/best en cas de non-échange (on regarde quelle diff est la plus avantageuse)
        if not echangeThisRound:
            iNextWorstBookScanned = B-1
            iNextBestBookNotScanned = 0
            for i in range(iBestBookNotScanned + 1, B):
                if not isThisBookScanned[bookOrderedByScore[i]] and bookOrderedByScore[i] in dictWhoHasThatBook.keys():
                    iNextBestBookNotScanned = i
                    break
            for i in range((B-iWorstBookScanned) + 1, B+1):
                if isThisBookScanned[bookOrderedByScore[-i]]:
                    iNextWorstBookScanned = B - i
                    break
            diffByLoweringBest = S[bookOrderedByScore[iNextBestBookNotScanned]] - S[bookOrderedByScore[iWorstBookScanned]]
            diffByHigheringWorst = S[bookOrderedByScore[iBestBookNotScanned]] - S[bookOrderedByScore[iNextWorstBookScanned]]
            
            if diffByLoweringBest > diffByHigheringWorst:
                iBestBookNotScanned = iNextBestBookNotScanned
            else:
                iWorstBookScanned = iNextWorstBookScanned
            
    
    return (score, libOrder)
    
## Main over


vMin = 0.5 # ICI LA PARTIE A MODIFIER
vMax = 2 # ICI LA PARTIE A MODIFIER
step = 0.1   # ICI LA PARTIE A MODIFIER

vTop = 0
scoreTop = 0
libTop = []
for v in linspace(vMin, vMax, step): 
    print("Valorisation testée : "+str(v))
    score, l = getScoreAndLibOrder(v)

    if score > scoreTop:
        scoreTop = score
        vTop = v
        libTop = l


print("Meilleure valeur de valorisation : "+str(vTop))
print("Score : "+str(scoreTop))

# parsing the output
f = open("outputs/" + inFile, 'a')
f.write(str(len(libTop)) + '\n')
for i in range(len(libTop)):
    f.write(str(libTop[i][0]) + " " + str(len(libTop[i][1])) + '\n')
    f.write(" ".join([str(x) for x in libTop[i][1]]) + '\n')
f.close()