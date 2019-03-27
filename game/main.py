from sys import exit
from direct.showbase.ShowBase import *
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import ClockObject, WindowProperties, NodePath
from panda3d.core import PointLight, Spotlight, AmbientLight
from random import randint
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
		self.props.setCursorHidden(True)
		base.camLens.setFov(80)
		base.camLens.setNear(0.002)
		base.camLens.setFar(20)

		base.win.requestProperties(self.props)
		base.win.setClearColor((0, 0, 0, 0))
		base.disableMouse()
		self.running = True
		#load sound, models and animations and shit here
		self.player = Cat()

		self.scene = loader.loadModel("assetsmodels/room1.bam")
		self.scene.reparentTo(render)

		#make the pile of money
		self.moneymodel = loader.loadModel("assetsmodels/money.bam")
		self.potstack = loader.loadModel("assets/moneystack.egg")
		self.moneystack = []
		pot = self.potstack.findAllMatches("money*")
		for p in range(pot.get_num_paths()):
			self.moneystack.append(NodePath("money_"+str(p)))
			self.moneystack[p].reparentTo(self.scene)
			self.moneystack[p].setPos(pot[p].getPos())
			self.moneystack[p].setHpr(pot[p].getHpr())
			self.moneymodel.instanceTo(self.moneystack[p])
			self.moneystack[p].hide()


		animations = {
			"idle":"assets/animations/cat-idle.egg",
			"take":"assets/animations/cat-take.egg",
			"survive":"assets/animations/cat-survive.egg",
		}




		self.playerA = Actor("assets/cat_shayden.egg", animations)
		self.playerA.setTwoSided(True)
		self.playerA.setPos((-1.222, -2.153, 0))
		self.playerA.setHpr((112,0,0))
		self.playerA.loop("idle")
		self.playerA.reparentTo(self.scene)

		self.playerB = Actor("assets/cat_bonbon.egg", animations)
		self.playerB.setTwoSided(True)
		self.playerB.loop("idle")
		self.playerB.reparentTo(self.scene)

		self.focus = self.playerB
		self.animation = "idle"
		self.animControl = self.focus.getAnimControl("idle")
		self.focus.exposeJoint(base.camera, "modelRoot", "camera")
		base.camera.reparentTo(self.focus)

		self.accept("escape", self.quit)
		self.accept("mouse1", self.t_a)
		self.accept("mouse3", self.t_b)
		self.choice = None
		self.playerTurn = True
		self.beurt = 0

		self.cash = 3
		self.pot = 0
		self.started = 0

		self.music = base.loader.loadSfx("audio/iknowjazz.ogg")
		self.music.setLoop(True)
		self.music.play()
		self.waiting = True
		self.bullets = 0
		self.aibullets = 0
		self.taskMgr.add(self.loop, "gameloop")

	def turn(self, player, anim):
		self.waiting = False
		self.focus.stopJoint("modelRoot", "camera")
		self.focus = player
		base.camera.reparentTo(self.focus)
		self.focus.exposeJoint(base.camera, "modelRoot", "camera")
		self.focus.play(anim)
		if anim == "idle":
			self.focus.loop("idle")
		self.animation = anim
		self.animControl = self.focus.getAnimControl(anim)

	def t_a(self):
		if self.waiting:
			self.choice = "a"

	def t_b(self):
		if self.waiting:
			self.choice = "b"

	def loop(self, task):
		if self.running:
			frame = self.animControl.getFrame()
			numframes = self.animControl.getNumFrames()
			bullet_frames = [300,320,344,367,391,412]

			if self.playerTurn:
				if self.animation == "idle":
					if self.choice == "b":
						if self.pot > 0:
							if self.beurt == 0:
								self.turn(self.playerB, "take")
								self.playerTurn = True
							else:
								self.turn(self.playerA, "take")
								self.playerTurn = False
							self.started = 1
					elif self.choice == "a":
						if self.started == 0:
							if self.cash > 0:
								self.pot += 1
								self.cash -= 1
								if self.pot > 6:
									self.cash += self.pot
									self.pot = 0
							else:
								self.cash += self.pot
								self.pot = 0
							for m, money in enumerate(self.moneystack):
								if m < self.pot:
									money.show()
								else:
									money.hide()

				elif self.animation == "take":
					if frame in bullet_frames:
						self.waiting = True
						self.animControl.stop()
						if self.choice == "a":
							self.bullets += 1
							self.animControl.play(frame+1, numframes)
						elif self.choice == "b":
							if self.bullets > self.aibullets:
								self.animControl.play(445, numframes)
					if frame > 650:
						self.waiting = True
						if frame == 683:
							self.animControl.stop()
						if self.choice == "a" or self.choice == "b":
							if randint(0,5) > self.bullets:
								print("lives", self.bullets)
								self.turn(self.focus, "survive")
							else:
								print("dies", self.bullets)
								self.turn(self.focus, "survive")
				elif self.animation == "survive":
					if frame == 115:
						self.turn(self.focus, "idle")
						self.turn(self.playerB, "idle")
						self.beurt += 1
						if self.beurt == 2:
							self.beurt = 0
						self.waiting = True
			else:
				#else it's the computer's turn
				if self.animation == "take":
					for f, fram in enumerate(bullet_frames):
						if f > self.bullets and fram == frame:
							self.animControl.play(445, numframes)
							self.aibullets = f
							self.bullets = 0
					if frame > 660:
							if randint(0,5) > self.aibullets:
								print("lives")
								self.turn(self.focus, "survive")
							else:
								print("dies")
								self.turn(self.focus, "survive")
				elif self.animation == "survive":
					if frame == 115:
						self.turn(self.focus, "idle")
						self.turn(self.playerB, "idle")
						self.beurt = 0
						self.waiting = True
						self.playerTurn = True
			self.choice = None
			return task.cont
		else:
			print("bye!")
			exit()

	def quit(self):
		self.running = False

game = Game()
game.run()
