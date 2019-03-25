from sys import exit
from direct.showbase.ShowBase import *
from direct.actor.Actor import Actor
from panda3d.core import ClockObject, WindowProperties, NodePath
from panda3d.core import PointLight, Spotlight, AmbientLight


def stringToTupleOfFloats(c):
	li = c.split(",")
	lf = []
	for l in li:
		lf.append(float(l))
	return tuple(lf)

def getLights(model, set=True):
	foundLights = {}
	foundLights["pointlights"] = model.findAllMatches('pointlight*')
	foundLights["spotlights"] = model.findAllMatches('spotlight*')
	foundLights["directionallights"] = model.findAllMatches('directionallight*')
	lights = {}
	for key in foundLights:
		ck = foundLights[key]
		lights[key] = []
		for i in range(ck.get_num_paths()):
			n = ck[i]
			lights[key].append(NodePath(PointLight(key+"_"+str(i))))
			color = stringToTupleOfFloats(n.getTag("color"))
			lights[key][i].setColor(color)
			lights[key][i].setPos(n.getPos())
			lights[key][i].reparentTo(render)
			if set:
				render.setLight(lights[key][i])
	return lights

class Cat():
	def __init__(self):
		self.lives = 9
		self.money = 100


class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		globalClock.setMode(ClockObject.MLimited)
		globalClock.setFrameRate(60)
		base.setFrameRateMeter(True)
		self.props = WindowProperties()
		self.props.setSize((1600, 900))
		self.props.setFullscreen(False)
		#self.props.setCursorHidden(True)
		base.win.requestProperties(self.props)
		#base.disableMouse()
		base.win.setClearColor((0,0,0,0))
		self.running = True
		#load sound, models and animations and shit here
		self.background = loader.loadModel("data/models/room1.egg")
		self.lights = getLights(self.background)

		self.background.reparentTo(render)
		self.animation = Actor("data/models/scene1.egg", {"test": "data/models/scene1-testmovement1.egg"})
		self.animation.loop("test")
		self.animation.reparentTo(render)
		self.player = Cat()
		self.taskMgr.add(self.loop, "gameloop")

	def loop(self, task):
		if self.running:
			self.accept("escape", self.quit)
			#game logic here (click on object to transition to animation?)
			return task.cont
		else:
			print("bye!")
			exit()

	def quit(self):
		self.running = False

game = Game()
game.run()
