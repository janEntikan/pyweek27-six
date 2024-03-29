from sys import exit
from direct.showbase.ShowBase import *
from direct.actor.Actor import Actor
from direct.interval.ActorInterval import ActorInterval
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import ClockObject, WindowProperties, NodePath
from panda3d.core import PointLight, Spotlight, AmbientLight,TextFont, TextNode
from random import randint
import pman.shim
import time


from panda3d.core import ConfigVariableString
ConfigVariableString("framebuffer-srgb","true").setValue("true")
ConfigVariableString("view-frustum-cull","false").setValue("false")
ConfigVariableString("interpolate-frames","true").setValue("true")

class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		deltatime = globalClock.getDt()
		globalClock.setMode(ClockObject.M_forced)
		globalClock.setFrameRate(60)
		render.setShaderAuto()
		self.props = WindowProperties()
		self.props.setSize((1600, 900))
		self.props.setFullscreen(False)
		self.props.setCursorHidden(True)
		self.props.setTitle("Six Shootin' Cats")
		base.win.requestProperties(self.props)
		base.win.setClearColor((0, 0, 0, 0))
		base.disableMouse()
		base.camLens.setFov(80)
		base.camLens.setNear(0.002)
		base.camLens.setFar(20)
		self.playSpeed = 1.5
		self.cats = [
			"sponey", "snotty", "bonbon", "belmo", "boris", "shayden"
		]
		self.cat_bios = [
			"SPONEY \n\n This guy grew up on a sidewalk in Noyoeek."+
			" He was taught the way of the cigar by an ex-marine."+
			" Now he slaves away his days in dingy cafes waiting for the big snag."+
			" The big bacon. The large wallet.\n\nLuck: 1\nCharisma: 3\nStyle: 1\nStamina: 1",
			"SNOTTY \n\n After an accident at one of his pooling tours he was forced to make ends meet "+
			"by doing unspeakable acts to old pussycat. Now that he's even too old for that "+
			"he's looking for redemption in the underbelly of this godforsaken town. "+
			"He dreams in neon coke signs.\n\nLuck: 2\nCharisma: 1\nStyle: 3\nStamina: 2",
			"BONBON \n\n The coolest beatnick to ever grace Purris. "+
			"He mostly writes proze about longing for the giant insects to inhabit his lonely road "+
			"that walks the lines of interzones and drop out dangerbelly summerjams."+
			"..and he's got aids.\n\nLuck: -2\nCharisma: 5\nStyle: 5\nStamina: -2",
			"BELMO \n\n He used to be a hobo-fighter untill he was invited here one rainy night. "+
			"Though he can't remember his backstory, it's easy to asume a couple of things: "+
			"He has a leak in his attic, he lost his marbles, he's out of his mind, "+
			"perma-fried and CRAZY!\n\nLuck: 5\nCharisma: 1\nStyle: 2\nStamina: -10",
			"BORIS \n\n Aaaah, Boris. The stoik ol' russian. His owner used to be a bourgeoise debutante "+
			"but after her death was forced to live on the street and suck high calliber magnums for insulin."+
			"He saved a baby's life one time.\n\nLuck: 5\nCharisma: 5\nStyle: 5\nStamina: 5",
			"SHAYDEN \n\n Not much is known about Shayden except that he's never lost a game of roulette, EVER! "+
			"Nobody invites him, he just shows up and whoops everyone's buttocks. "+
			"Some say he has a sixth-sense...\n\nLuck: ?\nCharisma: ?\nStyle: ?\nStamina: ?",
		]

		self.font = loader.loadFont('assets/fonts/Redkost Comic.otf')
		##self.font.render_mode = TextFont.RM_wireframe
		self.font.setPixelsPerUnit(100)
		self.creditstring = "BY TEAM MOMOJO (NL) for Pyweek27\n    momojo@rocketship.com\nArt/Design/Programming/Animation:\n   MOMOJOHOBO AKA Hendrik-Jan\nMusic: \n   MOMOJOMEERVALMEISJE AKA Skylar\nSfx:\n    MOMOJOJOEOJ AKA JoeBellamy\n"
		self.credits = self.addText(self.creditstring, -0.4, -2, 1.5)
		self.credits[0].setAlign(TextNode.ALeft)
		self.char_dest = self.addText("", 38, 2, 3)
		self.char_dest[0].setWordwrap(13)
		self.char_dest[0].setAlign(TextNode.ARight)
		self.statetext = self.addText("", 19, 5, 10)
		self.statetext[0].setWordwrap(13)
		self.statetext[0].setAlign(TextNode.ACenter)
		self.statetextb = self.addText("", 19, 7, 5)
		self.statetextb[0].setWordwrap(13)
		self.statetextb[0].setAlign(TextNode.ACenter)
		self.lives = 6
		self.choice_l = self.addText("", 0, 34, 3)
		self.choice_l[0].setAlign(TextNode.ALeft)
		self.choice_l[0].setTextColor((1,1,1,1))
		self.choice_r = self.addText("", 38, 34, 3)
		self.choice_r[0].setAlign(TextNode.ARight)
		self.choice_r[0].setTextColor((1,1,1,1))
		self.inactivecolor = (0.2,0.2,0.2,0.1)
		self.running = True
		#load sound, models and animations and shit here
		#self.scene = loader.loadModel("assetsmodels/room1.bam")
		#make players
		self.animations = {
			"idle":"assets/animations/cat-idle.egg",
			"take":"assets/animations/cat-take.egg",
			"survive":"assets/animations/cat-survive.egg",
			"die":"assets/animations/cat-die.egg",
			"angel": "assets/animations/cat-angel.egg",
			"win": "assets/animations/cat-win.egg",
			"kill_a": "assets/animations/cat-kill_a.egg",
			"kill_b": "assets/animations/cat-kill_b.egg",
			"select": "assets/animations/cat-select.egg",
			"pray": "assets/animations/cat-pray.egg",
			"victory": "assets/animations/cat-victory.egg",
			"credits": "assets/animations/cat-credits.egg",
		}

		self.sounds = {
			"click": loader.loadSfx("assets/audio/sfx_click.ogg"),
			"open": loader.loadSfx("assets/audio/sfx_open.ogg"),
			"close": loader.loadSfx("assets/audio/sfx_close.ogg"),
			"insert": loader.loadSfx("assets/audio/sfx_insert.ogg"),
			"shot": loader.loadSfx("assets/audio/sfx_shot.ogg"),
			"win": loader.loadSfx("assets/audio/sfx_win.ogg"),
			"lost": loader.loadSfx("assets/audio/sfx_lost.ogg"),
			"raise": loader.loadSfx("assets/audio/sfx_raise.ogg"),
			"reset": loader.loadSfx("assets/audio/sfx_reset.ogg"),
			"go": loader.loadSfx("assets/audio/sfx_go.ogg"),
			"smoke": loader.loadSfx("assets/audio/sfx_smoke.ogg"),
			"spin": loader.loadSfx("assets/audio/sfx_spin.ogg"),
			"pick": loader.loadSfx("assets/audio/sfx_pick.ogg"),
			"pickbullet": loader.loadSfx("assets/audio/sfx_pickbullet.ogg"),
			"survived": loader.loadSfx("assets/audio/sfx_survived.ogg"),
			"harp": loader.loadSfx("assets/audio/sfx_harp.ogg"),
			"harpdies": loader.loadSfx("assets/audio/sfx_harpdies.ogg"),
			"jawz": loader.loadSfx("assets/audio/sfx_jawz.ogg"),
		}
		try:
			save = open("savegame", "r")
			self.level = int(save.read())
		except:
			self.level = 1

		self.scene = loader.loadModel("assetsmodels/credits.bam")
		self.scene.reparentTo(render)
		self.crd = loader.loadModel("assets/models/credits.egg")
		self.crd.reparentTo(self.scene)
		self.playerB = Actor("assets/models/cat_boris.egg", self.animations)
		self.focus = self.playerB
		self.prevCat = "sponey"
		self.playerCat = "sponey"
		self.swap()
		self.turn(self.playerB, "credits", False)
		self.animControl.setPlayRate(1)

		self.started = 0
		self.accept("escape", self.quit)
		self.accept("mouse1", self.t_a)
		self.accept("mouse3", self.t_b)
		self.choice = None
		self.playerTurn = True
		self.beurt = 0

		self.music = base.loader.loadSfx("assets/audio/iknowjazz.ogg")
		self.music.setLoop(True)
		self.music.play()
		self.music.setVolume(0.5)
		self.waiting = True
		self.bullets = 0
		self.aibullets = 0
		self.taskMgr.add(self.loop, "gameloop")

	def addText(self, str, x, y, s=1):
		l = TextNode('textnode')
		l.setFont(self.font)
		l.setText(str)
		l.setShadow((0.03,0.03))
		l.setTextColor((0.5,0.5,0.5,1))
		l.setSmallCaps(True)
		textNodePath = render2d.attachNewNode(l)
		textNodePath.setScale(0.025*s)
		textNodePath.setPos(-0.95+(x/20),0,0.83-(y/20))
		return l, textNodePath

	def swap(self, player="b"):
		if player == "b":
			self.playerB.removePart("modelRoot")
			self.playerB.removeNode()
			self.playerB = Actor("assets/models/cat_"+self.playerCat+".egg", self.animations)
			self.playerB.setTwoSided(True)
			self.playerB.loop("select")
			self.playerB.reparentTo(self.scene)
			self.animControl = self.playerB.getAnimControl("idle")
			self.playerB.exposeJoint(base.camera, "modelRoot", "camera")
			base.camera.reparentTo(self.playerB)
		else:
			self.playerA.removePart("modelRoot")
			self.playerA = Actor("assets/models/cat_"+self.cats[self.level%6]+".egg", self.animations)
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
			if not self.animation == "credits":
				self.smoke.setH(self.smoke.getH()+0.2)
			frame = self.animControl.getFrame()
			numframes = self.animControl.getNumFrames()
			bullet_frames = [300,320,344,367,391,412]
			if self.playerTurn:
				if self.animation == "credits":
					if frame == 280:
						self.playerTurn = True
						self.waiting = True
						self.scene.removeNode()
						self.scene = loader.loadModel("assetsmodels/room1.bam")
						self.scene.reparentTo(render)
						self.smoke = loader.loadModel("assets/models/roomsmoke.egg")
						self.smoke.reparentTo(self.scene)
						self.playerB = Actor("assets/models/cat_"+self.playerCat+".egg", self.animations)
						self.swap()
						self.turn(self.playerB, "select", True)
						self.playerA = Actor("assets/models/cat_"+self.cats[self.level%6]+".egg", self.animations)
						self.playerA.setPos((-1.222, -2.153, 0))
						self.playerA.setHpr((112,0,0))
						self.swap("a")
						self.turn(self.playerA, "idle", True)
						self.smokeA = loader.loadModel("assets/models/smoke.egg")
						self.smokeA.setPos((-0.981571,-2.98202, 1.47267))
						self.smokeA.setHpr((134,0,0))
						self.smokeA.reparentTo(self.scene)
						self.smokeA.hide()
						self.smokeB = loader.loadModel("assets/models/smoke.egg")
						self.smokeB.setPos((-0.842, 0.09013, 1.50349))
						self.smokeB.reparentTo(self.scene)
						self.smokeB.hide()
						#make the piles of money
						self.charSelection = 0
						self.pot = 0
						self.moneymodel = loader.loadModel("assetsmodels/money.bam")
						self.potstack = loader.loadModel("assets/models/moneystack.egg")
						self.moneystack = []
						pot = self.potstack.findAllMatches("money*")
						for p in range(pot.get_num_paths()):
							self.moneystack.append(NodePath("money_"+str(p)))
							self.moneystack[p].reparentTo(self.scene)
							self.moneystack[p].setPos(pot[p].getPos())
							self.moneystack[p].setHpr(pot[p].getHpr())
							self.moneymodel.instanceTo(self.moneystack[p])
							self.moneystack[p].hide()
						self.cash_a = 6+(self.level*2)
						self.cash_b = 6
						self.stack_a = loader.loadModel("assets/models/playerstack.egg")
						self.stack_b = loader.loadModel("assets/models/playerstack.egg")
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
						self.turn(self.playerA, "idle", True)
						self.turn(self.playerB, "select", True)
						self.waiting = True

				if self.animation == "select":
					self.bullets = 0
					self.aibullets = 0
					self.credits[0].setText("")
					self.char_dest[0].setText(self.cat_bios[self.charSelection])
					self.choice_l[0].setText("(Left mouse button)\nSelect character")
					self.choice_r[0].setText("(Right mouse button)\nStart game")
					self.choice_r[0].setTextColor((1,1,1,1))
					if self.level == 1:
						self.choice_l[0].setTextColor(self.inactivecolor)
					else:
						self.choice_l[0].setTextColor((1,1,1,1))
					if self.choice == "a":
						if self.level > 1:
							self.charSelection += 1
							if self.charSelection >= self.level:
								self.charSelection = 0
							self.playerCat = self.cats[self.charSelection]
							self.swap()
					elif self.choice == "b":
						self.credits[0].setText("")
						self.char_dest[0].setText("")
						self.turn(self.playerA, "idle", True)
						self.turn(self.playerB, "idle", True)
						self.playerTurn = True
						self.waiting = True
				elif self.animation == "idle":
					self.choice_l[0].setTextColor((1,1,1,1))
					self.choice_r[0].setTextColor(self.inactivecolor)
					self.choice_l[0].setText("Raise bet")
					if not self.started == 0:
						self.choice_l[0].setTextColor(self.inactivecolor)
					self.choice_r[0].setText("Take shooter")
					if self.pot > 0:
						self.choice_r[0].setTextColor((1,1,1,1))
					else:
						self.choice_r[0].setTextColor(self.inactivecolor)
					if self.choice == "b":
						if self.pot > 0:
							self.choice_r[0].setTextColor((1,1,1,1))
							if self.beurt == 0:
								self.bullets = 0
								self.sounds["go"].play()
								self.turn(self.playerB, "take")
								self.playerTurn = True
							else:
								self.turn(self.playerA, "take")
								self.playerTurn = False
							self.choice_l[0].setText("")
							self.choice_r[0].setText("")
							self.started = 1
					elif self.choice == "a":
						if self.started == 0:
							if self.cash_b > 0:
								self.sounds["raise"].play()
								self.pot += 1
								self.cash_b -= 1
								if self.pot > 6:
									self.cash_b += self.pot
									self.pot = 0
							else:
								self.sounds["reset"].play()
								self.cash_b += self.pot
								self.pot = 0
							self.setMoney()

				elif self.animation == "take":
					if frame == 33:
						self.sounds["pick"].play()
					if frame == 111:
						self.sounds["open"].play()
					if frame == 250:
						self.sounds["pickbullet"].play()
					if frame == 530:
						self.sounds["jawz"].play()
					elif frame in bullet_frames:
						self.choice_l[0].setTextColor((1,1,1,1))
						self.choice_r[0].setTextColor(self.inactivecolor)
						if self.bullets > self.aibullets:
							b = self.bullets
						else:
							b = self.aibullets
						self.choice_l[0].setText("Raise stakes\ncurrently: "+ str(b))
						self.choice_r[0].setText("Close shooter")
						if self.bullets > self.aibullets:
							self.choice_r[0].setTextColor((1,1,1,1))
						self.waiting = True
						self.animControl.stop()
						if self.choice == "a":
							self.sounds["insert"].play()
							self.bullets += 1
							self.animControl.play(frame+1, numframes)
						elif self.choice == "b":
							if self.bullets > self.aibullets:
								self.animControl.play(445, numframes)
								self.choice_l[0].setText("")
								self.choice_r[0].setText("")
					elif frame == 450:
						self.sounds["close"].play()
					elif frame == 480:
						self.sounds["spin"].play()
					elif frame == 460:
						self.choice_l[0].setTextColor((1,1,1,1))
						self.choice_r[0].setTextColor((1,1,1,1))
						self.choice_l[0].setText("SPIN!")
						self.choice_r[0].setText("SPIN!")
						self.waiting = True
						self.animControl.stop()
						if self.choice == "a" or self.choice == "b":
							self.animControl.play(frame+1, numframes)
							self.choice_l[0].setText("")
							self.choice_r[0].setText("")
					elif frame > 650:
						self.choice_l[0].setTextColor((1,1,1,1))
						self.choice_r[0].setTextColor((1,1,1,1))
						self.choice_l[0].setText("FIRE!")
						self.choice_r[0].setText("FIRE!")
						self.waiting = True
						if frame == 683:
							self.animControl.stop()
						if self.choice == "a" or self.choice == "b":
							self.choice_l[0].setText("")
							self.choice_r[0].setText("")
							chamber = randint(1,6)
							if chamber > self.bullets:
								self.turn(self.focus, "survive")
							else:
								self.turn(self.focus, "die")
				elif self.animation == "survive" or self.animation == "die":
					if self.animation == "die":
						if frame == 78:
							self.smokeB.setScale(0.6)
							self.smokeB.hide()
							self.aibullets = 0
							self.bullets = 0
							self.cash_a += self.pot
							self.pot = 0
							self.setMoney()
							if self.cash_b <= 0:
								self.turn(self.playerB, "pray")
								self.turn(self.playerA, "kill_a")
								self.sounds["lost"].play()
								self.waiting = True
							else:
								self.turn(self.playerA, "idle", True)
								self.prevCat = self.playerCat
								self.playerCat = "angel"
								self.swap()
								self.turn(self.playerB, "angel", True)
								self.sounds["harp"].play()
								self.statetext[0].setText("LIVES: "+str(self.lives))
								self.lives -= 1
								self.statetext[0].setTextColor((1,1,1,1))
								#self.waiting = True
						elif frame == 22:
							self.sounds["shot"].play()
							self.sounds["smoke"].play()
							self.smokeB.show()
						elif frame > 22:
							self.smokeB.setScale(self.smokeB.getScale()+0.05)
					elif frame == 22:
						self.sounds["click"].play()
					elif frame == 94:
						self.sounds["survived"].play()
					elif frame == 115:
						self.turn(self.focus, "idle", True)
						self.beurt += 1
						self.turn(self.playerA, "take", True)
						self.playerTurn = False
				elif self.animation == "angel":
					self.started = 0
					if frame == 210:
						self.sounds["harp"].stop()
						self.sounds["harpdies"].play()
						self.statetext[0].setTextColor((1,0,0,1))
						if self.lives > 0:
							self.statetext[0].setText("LIVES: "+str(self.lives))
						else:
							self.statetext[0].setText("GAMEOVER")
					if frame > 262:
						self.playerCat = self.prevCat
						self.swap()
						self.statetext[0].setText("")
						if self.lives > 0:
							self.turn(self.playerA, "idle", True)
							self.turn(self.playerB, "idle", True)
							self.waiting = True
							self.started = 0
							self.playerTurn = True
							self.setMoney()
						else:
							self.pot = 0
							self.cash_a = 6+(self.level*2)
							self.cash_b = 6
							self.swap("a")
							self.started = 0
							self.playerTurn = True
							self.turn(self.playerA, "idle", True)
							self.turn(self.playerB, "select", True)
							self.lives = 6
							self.setMoney()
							self.waiting = True

				elif self.animation == "kill_a":
					self.statetext[0].setTextColor((1,0,0,1))
					self.statetext[0].setText("GONE BUST!")
					self.choice_l[0].setText("Aaaw")
					self.choice_r[0].setText("Aaaw")
					self.choice_l[0].setTextColor((1,1,1,1))
					self.choice_r[0].setTextColor((1,1,1,1))
					if frame == 88:
						self.sounds["shot"].play()
					if frame > 50:
						self.waiting = True
						if self.choice == "a" or  self.choice == "b":
							self.statetext[0].setText("")
							self.pot = 0
							self.cash_a = 6+(self.level*2)
							self.cash_b = 6
							self.swap("a")
							self.started = 0
							self.turn(self.playerA, "idle", True)
							self.turn(self.playerB, "select", True)
							self.lives = 6
							self.setMoney()
							self.waiting = True
			else:
				self.choice_l[0].setTextColor(self.inactivecolor)
				self.choice_r[0].setTextColor(self.inactivecolor)
				self.choice_l[0].setText("opponent's turn")
				self.choice_r[0].setText("opponent's turn")


				#else it's the computer's turn
				if self.animation == "take":
					for f, fram in enumerate(bullet_frames):
						if f > self.bullets and fram == frame:
							self.animControl.play(445, numframes)
					self.aibullets = self.bullets + 1
					if frame == 33:
						self.sounds["pick"].play()
					if frame == 111:
						self.sounds["open"].play()
					if frame == 250:
						self.sounds["pickbullet"].play()
					if frame in bullet_frames:
						self.sounds["insert"].play()
					elif frame == 450:
						self.sounds["close"].play()
					elif frame == 480:
						self.sounds["spin"].play()
					if frame == 530:
						self.sounds["jawz"].play()
					if frame > 660:
						chamber = randint(1,6)
						if chamber > self.aibullets:
							self.turn(self.focus, "survive")
						else:
							self.turn(self.focus, "die")
				elif self.animation == "survive" or self.animation == "die":
					if self.animation == "die":
						if frame == 78:
							self.smokeA.hide()
							self.smokeA.setScale(0.8)
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
						elif frame == 22:
							self.sounds["shot"].play()
							self.sounds["smoke"].play()
							self.smokeA.show()
						elif frame > 22:
							self.smokeA.setScale(self.smokeA.getScale()+0.05)
					elif frame == 22:
						self.sounds["click"].play()
					elif frame == 94:
						self.sounds["survived"].play()
					elif frame == 114:
						self.turn(self.focus, "idle", True)
						self.turn(self.playerB, "idle", True)
						self.beurt = 0
						self.playerTurn = True
						self.waiting = True
				elif self.animation == "kill_b":
					self.choice_l[0].setText("")
					self.choice_r[0].setText("")
					if frame == 88:
						self.sounds["shot"].play()
					if frame >= 150:
						if self.level == 6:
							self.turn(self.playerB, "victory", True)
							save = open("savegame", "w")
							save.write("1")
							self.statetext[0].setText("YOU WON\nTHE WHOLE\nGAME!\nWOW!")
							self.statetext[0].setTextColor((0,1,0,1))
						else:
							self.turn(self.playerB, "win", True)
							self.sounds["win"].play()
				elif self.animation == "victory":
					self.choice_l[0].setText("")
					self.choice_r[0].setText("")
				elif self.animation == "win":
					self.statetext[0].setTextColor((0,1,0,1))
					self.statetextb[0].setTextColor((0,1,0,1))
					self.statetext[0].setText("LEVEL UP!")
					self.statetextb[0].setText("You unlocked " + self.cats[self.level]+ "\nas a playable character")
					self.choice_l[0].setText("Hooray!")
					self.choice_r[0].setText("Hooray!")
					self.waiting = True
					if self.choice == "a" or self.choice == "b":
						self.statetext[0].setText("")
						self.statetextb[0].setText("")
						self.aibullets = 0
						self.bullets = 0
						self.level += 1
						save = open("savegame", "w")
						save.write(str(self.level))
						self.pot = 0
						self.cash_a = 6+(self.level*2)
						self.cash_b = 6
						self.swap("a")
						self.turn(self.playerA, "idle", True)
						self.turn(self.playerB, "select", True)
						self.lives = 6
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
