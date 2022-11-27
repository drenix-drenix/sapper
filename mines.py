import random, hashlib
from PIL import Image, ImageDraw

class MineGame:
	mines_count = 2
	wins_count = 0
		
	bet = 10
	game_map = [0] * 25
	
	mines = []
	opens = []
	
	gameid = 0
	
	def __init__(self, temp_mines_count, temp_bet):
		self.mines_count = temp_mines_count
		self.bet = temp_bet
		
		indexes = list(range(25))
		
		self.mines = []
		self.opens = []
		self.game_map = [0] * 25
		
		self.gameid = random.randint(10000000,99999999)
		random.seed(self.gameid)
		
		for i in range(self.mines_count):
			mine_index = random.choice(indexes)
			self.mines.append(mine_index)
			del indexes[indexes.index(mine_index)]
			self.game_map[mine_index] = 1
	
	def get_map_str(self):
		return "\n".join(
			["".join([str(self.game_map[x + (x2 * 5)]) for x in range(5)]) for x2 in range(5)]
		)
	
	def getresult(self):
		return "hardminea|" + str(random.randint(1000000,9999999)) + "-" + "|".join([str(x+1) for x in self.mines])
	
	def gethash(self):
		return hashlib.md5(self.getresult().encode("UTF-8")).hexdigest()
	
	def get_map_image(self, game_over):
		 image_map_mines = Image.new("RGBA", (640, 640), (255,255,255,255))
		 images = [
		 	Image.open("nothing.png"),
		 	Image.open("win.png"),
		 	Image.open("lose.png")
		 ]
		 for img in images:
		 	img.thumbnail((128,128))
		 
		 for y in range(5):
		 	for x in range(5):
		 		idx = y * 5 + x
		 		imageid = 0
		 		if game_over:
			 		if idx in self.mines:
			 			imageid = 2
			 		else:
			 			imageid = 1
		 		else:
		 			if idx in self.opens:
		 				imageid = 1
		 			else:
		 				imageid = 0
		 		
		 		image_map_mines.paste(images[imageid], (x * 128, y * 128))
		 image_map_mines.save("map.png")