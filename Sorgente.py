from z3 import *

#Classe riassuntiva
class mersenne_rng(object):
    def __init__(self, seed=1897):
        self.stato = [0]*624
        self.f = 1812433253
        self.m = 397
        self.u = 11
        self.s = 7
        self.b = 0x9D2C5680
        self.t = 15
        self.c = 0xEFC60000
        self.l = 18
        self.indice = 624
        self.lower_mask = (1 << 31)-1
        self.upper_mask = 1 << 31
        
        self.stato[0] = seed
        for i in range(1, 624):
            self.stato[i] = (self.f * (self.stato[i - 1] ^ (self.stato[i - 1] >> 30)) + i) & 0xFFFFFFFF
    
    def setStato(self,stato):
        self.indice=0
        self.stato=stato

    def setIndice(self,numero):
         self.indice=numero

    def twist(self):
        for i in range(624):
            temp = self.int_32(
                (self.stato[i] & self.upper_mask) + (self.stato[(i+1) % 624] & self.lower_mask))
            temp_shift = temp >> 1
            if temp % 2 != 0:
                temp_shift = temp_shift ^ 0x9908b0df
            self.stato[i] = self.stato[(i+self.m) % 624] ^ temp_shift
        self.indice = 0

    def temper(self, in_value):
        y = in_value
        y = y ^ (y >> self.u)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)
        return y

    def int_32(self, number):
        return 0xFFFFFFFF & number 
    
    def estrai_numero(self):
        if self.indice >= 624:
            self.twist()
        out = self.temper(self.stato[self.indice])
        self.indice += 1
        return self.int_32(out)
    
    def riavvolgi(self):
     for i in range(623,-1,-1):
        risultato = 0 

        tmp = self.stato[(i + 624) % 624]
        tmp ^= self.stato[(i + 397) % 624]

        if((tmp & self.upper_mask) == self.upper_mask):
            tmp ^= 0x9908b0df
        
        risultato = (tmp << 1) & self.upper_mask

        tmp = self.stato[(i + 623) % 624]
        tmp ^= self.stato[(i + 396) % 624]
        if((tmp & self.upper_mask) == self.upper_mask):
            tmp ^= 0x9908b0df
            risultato |= 1
        
        risultato |= (tmp << 1) & 0x7fffffff
        self.stato[i] = risultato

#Metodi di attacco
def rivela_stato(numeri):
        stato = []
        for n in numeri[:624]:
            stato.append(untemper(n)) 
        return stato

def untemper(out):
        y1 = BitVec('y1', 32)
        y2 = BitVec('y2', 32)
        y3 = BitVec('y3', 32)
        y4 = BitVec('y4', 32)
        y = BitVecVal(out, 32)
        s = Solver()
        equations = [
            y2 == y1 ^ (LShR(y1, 11)),
            y3 == y2 ^ ((y2 << 7) & 0x9D2C5680),
            y4 == y3 ^ ((y3 << 15) & 0xEFC60000),
            y == y4 ^ (LShR(y4, 18))
        ]
        s.add(equations)
        s.check()
        return s.model()[y1].as_long()

def main1():
    #Inizializzo i generatori
    prng = mersenne_rng(1897)
    prng_c = mersenne_rng()
    listaNumeriRandom = []

    #Copio lo stato
    for i in range(624):
        numEst=prng.estrai_numero()
        listaNumeriRandom.append(numEst) 
    stato_copiato = rivela_stato(listaNumeriRandom)
    
    #Lo inserisco in un prng nuovo
    prng_c.setStato(stato_copiato)
    prng_c.setIndice(624)

    risultati=[]
    #I risultati saranno gli stessi
    for i in range(3):
        risultati.append((prng.estrai_numero(),prng_c.estrai_numero()))    
    print(risultati)

def main2():    
    prng = mersenne_rng(1897)
    for i in range(624):
        prng.estrai_numero()
    print(prng.stato[0:3],"Vecchio stato")
    for i in range(624):
        prng.estrai_numero()
    print(prng.stato[0:3],"Nuovo stato")
    prng.riavvolgi()
    print(prng.stato[0:3],"Vecchio stato")

main2()