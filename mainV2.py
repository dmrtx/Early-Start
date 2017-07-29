import Tkinter as tk
import tkFileDialog as filedialog
import time

#Declara las variables para sacar el tiempo
numTareas = 0
numRecursos = 0
disRecurso = 0
listaTareas = []
listTareasNodos = []
nodosCompletados = []
colaNodos = []
resultNodos = []
start_time = 0


class nodo:
    nextNodos = []
    previousNodos = []
    isAdded = False
    isCompleted = False
    tiempoAcumulado = 0
    startTime = 0
    def __init__(self, duracion=None, recursos=None, numTarea = None):
        self.duracion = duracion
        self.recursos = recursos
        self.nextNodos = []
        self.previousNodos = []
        self.numTarea = numTarea
        self.tiempoAcumulado = int(duracion)

    def addNext(self, nextNode):
        self.nextNodos.append(nextNode)

    def addPrevious(self, prevNode):
        self.previousNodos.append(prevNode)

    def setStartTime(self, inicioTime):
        self.startTime = inicioTime

    def setEndTime(self, finTime):
        self.endTime = finTime

    def setAdded(self, bAgregado):
        self.isAdded = bAgregado

    def setCompleted(self, bCompletado):
        self.isCompleted = bCompletado

    def addTime(self,time):
        self.tiempoAcumulado = self.tiempoAcumulado +  int(time);

    def __repr__(self):
        return "#"+str(self.numTarea)+ " D: "+self.duracion + " R: " + self.recursos + " Tiempo Finalizacion:  " + str(self.tiempoAcumulado)

def readTxtFile():
    #Mostrar una pantalla de seleccion del archivo
    root = tk.Tk();
    root.withdraw();
    file_path = filedialog.askopenfilename();

    #Recuperar las lineas del archivo de texto
    with open(file_path) as f:
        content = f.readlines()

    #Recuperar al primera linea y ver el numero de tareas, numero de recursos, disposicion de recursos
    conLine1 = content[0].replace("\n","").split('\t')
    conLine2 = content[1].replace("\n","").split('\t')
    global numTareas, numRecursos, disRecurso, start_time
    start_time = time.time()
    numTareas = int(conLine1[0])
    numRecursos = int(conLine1[1])
    disRecurso = int(conLine2[1])

    #Recuperar las tareas y crear una lista con estas
    global listaTareas
    for i in range(2,(numTareas+2),1):
        listaTareas.append(content[i].replace("\n","").split('\t'))

    #Crear nodos para crear una representacion de
    global listTareasNodos
    for i in range(0,numTareas,1):
        listTareasNodos.append(nodo(listaTareas[i][0],listaTareas[i][1],i))

    #Crear las relaciones de los nodos
    for i in range(0, numTareas, 1):
        # print "Nodo: " + str(listTareasNodos[i]) + " Tiene los siguientes"
        for j in range(0,int(listaTareas[i][2]),1):
            #Agregar los nodos siguientes a un nodo
            listTareasNodos[i].addNext(listTareasNodos[int(listaTareas[i][j+3])-1])
            #Agregar los nodos anteriores al siguiente
            listTareasNodos[int(listaTareas[i][j + 3]) - 1].addPrevious(listTareasNodos[i])
            # print "Siguiente: " + str(listTareasNodos[int(listaTareas[i][j+3])-1])

def resolverEarlyStart():
    global colaNodos, nodosCompletados, resultNodos
    colaNodos = listTareasNodos[0].nextNodos
    #Mientras no se hayan completados los nodos no se termina
    while (isAgregadosTodos() == False):
        #Recupear el nodo con la duracion minima dentro de la cola de nodos
        minNodosCola = getMinNodo()
        #Agregar el nodo a la lista de nodos completados y marcar como completado
        for minNodoCola in minNodosCola:
            nodosCompletados.append(minNodoCola)
            minNodoCola.setCompleted(True)
            #Eliminar el nodo completado del nodo cola
            colaNodos.remove(minNodoCola)
            #Recuperar los nodos siguientes al nodo minimo y determinar cuales cumplen la condicion para ser agregados
            nodosCandidatos = minNodoCola.nextNodos
            # Agrega los nodos que cumplen las condiciones de la lista nodos completados
            for i in range(0, len(nodosCandidatos), 1):
                if (set(nodosCandidatos[i].previousNodos) <= set(nodosCompletados)):
                    nodosCandidatos[i].addTime(minNodoCola.tiempoAcumulado)
                    colaNodos.append(nodosCandidatos[i])
        #Guardar la iteracion para ver los recursos usados
        resultNodos.append(list(colaNodos))
        if (colaNodos[0] == listTareasNodos[-1]):
            break;
    #Mostrar los resultados
    printResult()
    printDetails()



#Comprueba que todos los nodos se haya agregado
def isAgregadosTodos():
    for i in range(1, numTareas,1):
        if (listTareasNodos[i].isCompleted == False):
            return False
    return True

#Imprimir los resultados
def printResult():
    print "\tResultados del algoritmo"
    for i in range(0, len(nodosCompletados)):
        print "\t#"+str(nodosCompletados[i].numTarea) + ", \tDuracion: "+nodosCompletados[i].duracion + ", \tRecursos: "+nodosCompletados[i].recursos + ", \tTiempo Inicio: " + str(nodosCompletados[i].tiempoAcumulado - int(nodosCompletados[i].duracion )) + ", \tTiempo Finalizacion: " + str(nodosCompletados[i].tiempoAcumulado)
    print "\n"

#Imprimir los rangos donde se pasa el numero de recursos
def printDetails():
    print "\tUso de recursos con conflictos"
    #Recorrer los resultados de cada iteracion para buscar cuando se pasa del numero de recursos usados
    for cola in resultNodos:
        numResIteration = 0;
        #Recuperar el maximo numero de recursos usados en la iteracion
        for i in cola:
            numResIteration = numResIteration + int(i.recursos)
        #Mostrar los recursos mas usados
        if (numResIteration> disRecurso):
            print "\tRecursos utilizados: " + str(numResIteration) + ", Inicio: "+ str(cola[-1].tiempoAcumulado - int(cola[-1].duracion))

#Recupera nodo minimo de la lista de nodos de trabajo, ese seria el que ya ha finalizado en un punto
def getMinNodo():
    numNodosCola = len(colaNodos)
    minNodos = []
    # Recupeara el un primero nodo que no haya sido agregado para comparar
    min = colaNodos[0]
    #Recuperar el nodo minimo que no haya sido agregado
    for i in range(0,numNodosCola,1):
        if (min.tiempoAcumulado > colaNodos[i].tiempoAcumulado):
            min = colaNodos[i]
    #Agregar los nodos que tienen el mismo tiempo acumulado minimo
    for i in range(0, numNodosCola, 1):
        if (colaNodos[i].tiempoAcumulado == min.tiempoAcumulado):
            minNodos.append(colaNodos[i])
    return minNodos

#Imprimir una lista
def printList(listNodos):
    print ''
    for item in listNodos:
        print item
    print ''

if __name__ == "__main__":
    readTxtFile()
    resolverEarlyStart()
    print "Tiempo de ejecucion: "+ str(time.time() - start_time)