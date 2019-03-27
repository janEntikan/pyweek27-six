from sys import exit
from direct.showbase.ShowBase import *
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import ClockObject, WindowProperties, NodePath
from panda3d.core import PointLight, Spotlight, AmbientLight
import pman.shim


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
		deltatime = globalClock.getDt()

		globalClock.setFrameRate(60)
		pman.shim.init(self)
		render.setShaderAuto()
		base.setFrameRateMeter(True)
		self.props = WindowProperties()
		self.props.setSize((1600, 900))
		self.props.setFullscreen(False)
		#self.props.setCursorHidden(True)
		base.win.requestProperties(self.props)
		base.win.setClearColor((0, 0, 0, 0))
		base.disableMouse()
		self.running = True
		#load sound, models and animations and shit here
		self.player = Cat() #basically holds score

		self.scene = loader.loadModel("assetsmodels/room1.bam")
		self.scene.reparentTo(render)

		animations = {
			"idle":"assets/animations/cat-idle_1.egg",
		}

		self.playerA = Actor("assets/cat_sponey.egg", animations)
		self.playerA.setPos((-1.222, -2.153, 0))
		self.playerA.setHpr((112,0,0))
		self.playerA.play("idle")
		self.playerA.reparentTo(self.scene)

		self.playerB = Actor("assets/cat_snotty.egg", animations)
		self.playerB.play("idle")
		self.playerB.reparentTo(self.scene)
		self.playerB.exposeJoint(base.cam, 'modelRoot', "camera")

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
