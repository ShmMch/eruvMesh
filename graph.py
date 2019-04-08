import networkx as nx
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from node_mapping import recursive_node_mapping

class Graph:
    def __init__(self):
        self.nodesData={}
        self.labels={}
        self.G = nx.Graph()
        self.G.add_node(1)
        self.figure = nx.draw(self.G)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

    def buildNetworkxGraph(self, meshString):
        graph = nx.Graph()
        try:
            jsonString = json.loads(meshString)
        except ValueError:
            print('Not a valid JSON Object')

        # If mesh string is empty, draw node 'Me' only
        if (jsonString.__len__() == 0):
            graph.add_node('Me')
        else:
            recursive_node_mapping(jsonString, 'Me', graph)

        return graph

    def drawMesh(self, meshString):
        self.figure.clear()
        self.G = self.buildNetworkxGraph(meshString)
        val_map = {'Me': 'gold'}
        values = [val_map.get(node, 'violet') for node in self.G.nodes()]
        self.pos = nx.spring_layout(self.G)
        self.figure = nx.draw(self.G, self.pos, node_size=500, with_labels=True, node_color=values, width=1, edge_color='lightblue',
                     font_weight='regular', font_family='Trebuchet MS', font_color='black')
        self.canvas.draw()

    def updateNodes(self, meshString):
        self.drawMesh(meshString)
    
    def updateNodeData(self, nodeDataString):
        nodeData = json.loads(nodeDataString)['SendData']
        oldNodeData = self.nodesData[nodeData['MeshId']] if nodeData['MeshId'] in self.nodesData else ''

        if(not str(oldNodeData)==str(nodeData)):
            nodeData['label']='Prev: ' + str(nodeData['isPrevConnected'] )+ '\nNext: ' + str(nodeData['isNextConnected'] )
            self.nodesData[nodeData['MeshId']]=nodeData
            self.labels[nodeData['MeshId']]=nodeData['label']
            color_map = []
            for node in self.G:
                if(not node in self.labels):
                    self.labels[node] = node
                if node in self.nodesData:
                    color_map.append('green' if self.nodesData[node]['isPrevConnected'] and self.nodesData[node]['isNextConnected'] else 'red')
                else:
                     color_map.append('gray')
            pos = nx.spring_layout(self.G)
            self.figure.clear()
            self.figure = nx.draw(self.G,pos=pos,node_color = color_map,with_labels = False)
            nx.draw_networkx_labels(self.G,pos,self.labels,font_size=12)
            self.canvas.draw()

