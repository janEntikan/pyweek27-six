from sys import exit
from direct.showbase.ShowBase import *
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import ClockObject, WindowProperties, NodePath
from panda3d.core import PointLight, Spotlight, AmbientLight
from random import randint
import pman.shim


from panda3d.core import ConfigVariableString
ConfigVariableString("framebuffer-srgb","true").setValue("true")
ConfigVariableString("view-frustum-cull","false").setValue("false")
ConfigVariableString("interpolate-frames","true").setValue("true")

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
		self.scene = loader.loadModel("assetsmodels/room1.bam")
		self.scene.reparentTo(render)
		#make players
		self.animations = {
			"idle":"assets/animations/cat-idle.egg",
			"take":"assets/animations/cat-take.egg",
			"survive":"assets/animations/cat-survive.egg",
			"die":"assets/animations/cat-die.egg",
			"win": "assets/animations/cat-win.egg",
			"kill_a": "assets/animations/cat-kill_a.egg",
			"kill_b": "assets/animations/cat-kill_b.egg",
			"select": "assets/animations/cat-select.egg",
			"pray": "assets/animations/cat-pray.egg",
			"victory": "assets/animations/cat-victory.egg",
		}
		self.playSpeed = 2.5
		self.cats = [
			"sponey", "snotty", "bonbon", "belmo", "boris", "shayden"
		]
		self.level = 1
		self.playerCat = "sponey"
		self.playerA = Actor("assets/cat_"+self.cats[self.level%6]+".egg", self.animations)
		self.playerA.setTwoSided(True)
		self.playerA.setPos((-1.222, -2.153, 0))
		self.playerA.setHpr((112,0,0))
		self.playerA.loop("idle")
		self.playerA.reparentTo(self.scene)
		self.playerB = Actor("assets/cat_"+self.playerCat+".egg", self.animations)
		self.playerB.setTwoSided(True)
		self.playerB.loop("win")
		self.playerB.reparentTo(self.scene)
		self.focus = self.playerB
		self.animation = "select"
		self.animControl = self.focus.getAnimControl("idle")
		self.animControl.setPlayRate(self.playSpeed)
		self.focus.exposeJoint(base.camera, "modelRoot", "camera")
		base.camera.reparentTo(self.focus)
		self.charSelection = 0

		#make the piles of money
		self.pot = 0
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

		self.cash_a = 6
		self.cash_b = 6
		self.stack_a = loader.loadModel("assets/playerstack.egg")
		self.stack_b = loader.loadModel("assets/playerstack.egg")
		self.moneystack_a = []
		self.moneystack_b = []
		s1 = self.stack_a.findAllMatches("money*")
		s2 = self.stack_b.findAllMatches("money*")

		for p in range(s1.get_num_paths()):
			self.moneystack_a.append(NodePath("money_"+str(p)))
			self.moneystack_a[p].reparentTo(self.scene)
			self.moneystack_a[p].setPos(self.playerA, s1[p].getPos())
			self.moneystack_a[p].setX(self.moneystack_a[p].getX()+2)
			self.moneystack_a[p].setY(self.moneystack_a[p].getY()-0.7)
			self.moneystack_a[p].setHpr(self.playerA, s1[p].getHpr())
			self.moneymodel.instanceTo(self.moneystack_a[p])
			self.moneystack_a[p].hide()
			self.moneystack_b.append(NodePath("money_"+str(p)))
			self.moneystack_b[p].reparentTo(self.scene)
			self.moneystack_b[p].setPos(render, s2[p].getPos())
			self.moneystack_b[p].setHpr(render, s2[p].getHpr())
			self.moneystack_b[p].setX(self.moneystack_b[p].getX())
			self.moneystack_b[p].setY(self.moneystack_b[p].getY()-1)
			self.moneymodel.instanceTo(self.moneystack_b[p])
			self.moneystack_b[p].hide()

		for m, mon in enumerate(self.moneystack_a):
			if m < self.cash_a:mon.show()
			else:mon.hide()
		for m, mon in enumerate(self.moneystack_b):
			if m < self.cash_b:mon.show()
			else:mon.hide()

		self.started = 0
		self.accept("escape", self.quit)
		self.accept("mouse1", self.t_a)
		self.accept("mouse3", self.t_b)
		self.choice = None
		self.playerTurn = True
		self.beurt = 0

		self.music = base.loader.loadSfx("audio/iknowjazz.ogg")
		self.music.setLoop(True)
		self.music.play()
		self.waiting = True
		self.bullets = 0
		self.aibullets = 0
		self.taskMgr.add(self.loop, "gameloop")

	def swap(self, player="b"):
		if player == "b":
			self.playerB.removePart("modelRoot")
			self.playerB = Actor("assets/cat_"+self.playerCat+".egg", self.animations)
			self.playerB.setTwoSided(True)
			self.playerB.loop("select")
			self.playerB.reparentTo(self.scene)
			self.animControl = self.playerB.getAnimControl("idle")
			self.playerB.exposeJoint(base.camera, "modelRoot", "camera")
			base.camera.reparentTo(self.playerB)
		else:
			self.playerA.removePart("modelRoot")
			self.playerA = Actor("assets/cat_"+self.cats[self.level%6]+".egg", self.animations)
			self.playerA.setPos((-1.222, -2.153, 0))
			self.playerA.setHpr((112,0,0))
			self.playerA.setTwoSided(True)
			self.playerA.loop("idle")
			self.playerA.reparentTo(self.scene)
			self.animControl = self.playerA.getAnimControl("idle")
			self.playerA.exposeJoint(base.camera, "modelRoot", "camera")
			base.camera.reparentTo(self.playerA)
		self.animControl.setPlayRate(self.playSpeed)

	def turn(self, player, anim, loop=False):
		self.waiting = False
		self.focus.stopJoint("modelRoot", "camera")
		self.focus = player
		base.camera.reparentTo(self.focus)
		self.focus.exposeJoint(base.camera, "modelRoot", "camera")
		print(anim, loop)
		if loop == True:
			self.focus.loop(anim)
		else:
			self.focus.play(anim)
		self.animation = anim
		self.animControl = self.focus.getAnimControl(anim)
		self.animControl.setPlayRate(self.playSpeed)

	def setMoney(self):
		for m, money in enumerate(self.moneystack):
			if m < self.pot: money.show()
			else: money.hide()
		for m, mon in enumerate(self.moneystack_a):
			if m < self.cash_a:mon.show()
			else:mon.hide()
		for m, mon in enumerate(self.moneystack_b):
			if m < self.cash_b:mon.show()
			else:mon.hide()

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
				if self.animation == "select":
					if self.choice == "a":
						if self.level > 1:
							self.charSelection += 1
							if self.charSelection >= self.level:
								self.charSelection = 0
							self.playerCat = self.cats[self.charSelection]
							self.swap()
					elif self.choice == "b":
						self.turn(self.playerA, "idle", True)
						self.turn(self.playerB, "idle", True)
						self.playerTurn = True
						self.waiting = True
				elif self.animation == "idle":
					if self.choice == "b":
						if self.pot > 0:
							if self.beurt == 0:
								self.bullets = 0
								self.turn(self.playerB, "take")
								self.playerTurn = True
							else:
								self.turn(self.playerA, "take")
								self.playerTurn = False
							self.started = 1
					elif self.choice == "a":
						if self.started == 0:
							if self.cash_b > 0:
								self.pot += 1
								self.cash_b -= 1
								if self.pot > 6:
									self.cash_b += self.pot
									self.pot = 0
							else:
								self.cash_b += self.pot
								self.pot = 0
							self.setMoney()

				elif self.animation == "take":
					if frame in bullet_frames:
						self.waiting = True
						self.animControl.stop()
						if self.choice == "a":
							self.bullets += 1
							print("adding bullet, theres ", self.bullets)
							self.animControl.play(frame+1, numframes)
						elif self.choice == "b":
							if self.bullets > self.aibullets:
								self.animControl.play(445, numframes)
					elif frame == 460:
						self.waiting = True
						self.animControl.stop()
						if self.choice == "a":
							self.animControl.play(frame+1, numframes)
					elif frame > 650:
						self.waiting = True
						if frame == 683:
							self.animControl.stop()
						if self.choice == "a" or self.choice == "b":
							chamber = randint(1,6)
							print(chamber, self.bullets)
							if chamber > self.bullets:
								self.turn(self.focus, "survive")
							else:
								self.turn(self.focus, "die")
				elif self.animation == "survive" or self.animation == "die":
					if self.animation == "die":
						if frame == 78:
							self.aibullets = 0
							self.bullets = 0
							self.cash_a += self.pot
							self.pot = 0
							self.setMoney()
							if self.cash_b <= 0:
								self.turn(self.playerB, "pray")
								self.turn(self.playerA, "kill_a")
								self.waiting = True
							else:
								self.turn(self.playerA, "idle", True)
								self.turn(self.playerB, "idle", True)
								self.started = 0
								self.waiting = True
					elif frame == 115:
						self.turn(self.focus, "idle", True)
						self.beurt += 1
						self.turn(self.playerA, "take", True)
						self.playerTurn = False
				elif self.animation == "kill_a":
					if frame > 50:
						self.waiting = True
						if self.choice == "a":
							self.pot = 0
							self.cash_a = 6+(self.level*2)
							self.cash_b = 6
							self.swap("a")
							self.started = 0
							self.turn(self.playerA, "idle", True)
							self.turn(self.playerB, "select")
							self.setMoney()
							self.waiting = True
				elif self.animation == "win":
					print("cool")
			else:
				#else it's the computer's turn
				if self.animation == "take":
					for f, fram in enumerate(bullet_frames):
						if f > self.bullets and fram == frame:
							self.animControl.play(445, numframes)
							self.aibullets = f
							self.bullets = 0
					if frame > 660:
							if randint(1,1) > self.aibullets: #CHANGE HERE!
								self.turn(self.focus, "survive")
							else:
								self.turn(self.focus, "die")
				elif self.animation == "survive" or self.animation == "die":
					if self.animation == "die":
						if frame == 78:
							self.cash_a -= self.pot
							self.cash_b += self.pot*2
							self.pot = 0
							self.setMoney()
							if self.cash_a <= 0:
								self.turn(self.playerA, "pray")
								self.turn(self.playerB, "kill_b")
							else:
								self.turn(self.playerA, "idle", True)
								self.turn(self.playerB, "idle", True)
								self.beurt = 0
								self.started = 0
								self.playerTurn = True
								self.waiting = True
							self.bullets = 0
							self.aibullets = 0

					elif frame == 114:
						self.turn(self.focus, "idle", True)
						self.turn(self.playerB, "idle", True)
						self.beurt = 0
						self.playerTurn = True
						self.waiting = True
				elif self.animation == "kill_b":
					print(frame)
					if frame >= 150:
						if self.level == 7:
							self.turn(self.playerB, "victory", True)
						else:
							self.turn(self.playerB, "win", True)
				elif self.animation == "win":
					print("win!")
					self.waiting = True
					if self.choice == "a" or self.choice == "b":
						self.aibullets = 0
						self.bullets = 0
						self.level += 1
						self.pot = 0
						self.cash_a = 6+(self.level*2)
						self.cash_b = 6
						self.swap("a")
						self.turn(self.playerA, "idle", True)
						self.turn(self.playerB, "select", True)
						self.setMoney()
						self.started = 0
						self.playerTurn = True
						self.waiting = True
						self.beurt = 0
			if self.beurt == 2:
				self.beurt = 0
			self.choice = None
			return task.cont
		else:
			print("bye!")
			exit()

	def quit(self):
		self.running = False

game = Game()
game.run()
