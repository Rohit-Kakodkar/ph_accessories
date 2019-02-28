import numpy as np
from scipy.linalg import eigvals
import matplotlib.pyplot as plt

class ph_accessories :
    
    def __latgen(ibrav, cell_dm, at):
        
        '''
            Convinience function to obtain lattice vectors
        '''

        if (ibrav > 4) :
            raise ValueError('Lattice type not supported. Only ibav = 1-4 are supported')

        if (ibrav==0) :
            if ((np.sum(np.sqrt(at[:,1])) == 0) or 
                (np.sum(np.sqrt(at[:,2])) == 0) or 
                (np.sum(np.sqrt(at[:,3])) == 0))  :
                raise ValueError('Error in input data at lattice generation. check input')

            if (cell_dm[0] != 0):
                at = at * cell_dm[0]

            if (cell_dm[0] <= 0) :
                raise ValueError('Error in input data at lattice generation. Check input.')

        if (ibrav==1):
            at[0,0] = cell_dm[0]
            at[1,1]	= cell_dm[0]
            at[2,2]	= cell_dm[0]
        elif (ibrav == 2) :
            term = np.float32(cell_dm[0]/2.0)
            at[0,0] = -term
            at[0,2] = term
            at[1,1] = term
            at[1,2] = term
            at[2,0] = -term
            at[2,1] = term
        elif (ibrav == 3):
            term = cell_dm[0]/2.0
            for ir in range(1,3) :
                at[0,ir] = term
                at[1,ir] = term
                at[2,ir] = term

            at[1,0] = -term
            at[2,0] = -term
            at[2,1] = -term
        elif (ibrav	== 4) :
            if (cell_dm[3] <= 0.0) :
                raise ValueError('Error in input data at lattice generation. Check input.')	

            cbya = cell_dm[3]
            at[0,0] = cell_dm[1]
            at[1,0] = -cell_dm[1]/2.0
            at[1,1] = np.sqrt(3)*cell_dm[1]/2.0
            at[2,2] = cell_dm[1]*cbya

        omega = np.linalg.det(at)

        return at, omega
    
    def __readfc(File_input):
        
        '''
           Convinience function to read *.fc files generated by Quantum Espresso 
        '''
        
        amu_ry = 911.444242132

    # Read the file line by line
        with open(File_input, 'r') as file :

            line = file.readline().split()

            ntyp = int(line[0])
            nat = int(line[1])
            ibrav = int(line[2])
            cell_dm = np.array(list(map(float, line[3:])))

            at = np.zeros([3,3])

            amass = np.zeros(ntyp)

            at, omega = ph_accessories.__latgen(ibrav, cell_dm, at)

            alat = cell_dm[0]
            at = at / alat
            
            for nt in range(ntyp):
                line = file.readline().split()
                            
                i = float(line[0])
                atm = line[1]
                amass_from_file = float(line[3])

                if (amass[nt] == 0.0) :
                    amass[nt] = amass_from_file/amu_ry

            ityp = np.zeros(nat)
            tau = np.zeros([3,nat])
            for na in range(nat):
                line = file.readline().split()

                i = int(line[0])
                ityp[na] = int(line[1])-1
                ityp[na] = int(ityp[na])
                tau[:,na] = np.array(list(map(float,line[2:])))


            has_zstar = file.readline()

            if (has_zstar == 'T') :
                has_zstar = True
            elif (has_zstar == 'F') :
                has_zstar = False

            epsil = np.zeros([3,3])
            for ir in range(3) :
                line = file.readline().split()
                epsil[:,ir] = np.array(list(map(float,line)))

            zeu = np.zeros([3,3,nat])
            for na in range(nat) :
                line = file.readline()
                for ir in range(3) :
                    line = file.readline().split()
                    zeu[:,ir,na] = np.array(list(map(float,line)))

            line = file.readline().split()

            nr1, nr2, nr3 = list(map(int,line)) 
            
            frc = np.zeros([nr1, nr2, nr3, 3, 3, nat, nat])

            while True :

                line = file.readline()

                if not line :
                    break

                ibid, jbid, nabid, nbbid = map(int,line.split())

                for m3 in range(nr3) :
                    for m2 in range(nr2) :
                        for m1 in range(nr1) :

                            line = file.readline()

                            (frc[m1,m2,m3,
                                 ibid-1,jbid-1,
                                 nabid-1,nbbid-1]) = np.round(float
                                                         (line.split()[3]), decimals=6)

        return (ntyp, nat, ityp, at, tau, amass, omega, has_zstar, epsil, zeu, 
            nr1, nr2, nr3, frc)
    
    def recips(self):
        
        '''
            Calculate reciprocal lattice vectors
            
            return value: self.bg
        '''

        prefactor = 1.0/np.linalg.det(self.at)
        b1 = prefactor*np.cross(self.at[1,:], self.at[2,:])
        b2 = prefactor*np.cross(self.at[2,:], self.at[0,:])
        b3 = prefactor*np.cross(self.at[0,:], self.at[1,:])

        self.bg = np.vstack([b1, b2, b3])
        
    def __wsinit(self):
        
        '''
            Convinience function to initialize WS cell        
        '''

        self.__atws = np.zeros([3,3])
        self.__atws[0,:] = self.at[0,:]*self.nr1
        self.__atws[1,:] = self.at[1,:]*self.nr2
        self.__atws[2,:] = self.at[2,:]*self.nr3
        self.__rws = np.zeros([4, self.__nrwsx])
        
        
        ii = 0
        nx = 2

        for ir in range(-nx, nx+1):
            for jr in range(-nx, nx+1):
                for kr in range(-nx, nx+1):
                    for i in range(1,4):
                        self.__rws[i,ii] = (self.__atws[0,(i-1)]*ir + self.__atws[1,(i-1)]*jr +
                                            self.__atws[2,(i-1)]*kr)

                    self.__rws[0,ii] = (self.__rws[1,ii]**2 + self.__rws[2,ii]**2 + 
                                        self.__rws[3,ii]**2)
                    self.__rws[0,ii] = np.float32(0.50)*self.__rws[0,ii]
                    if (self.__rws[0,ii] > 1e-6):
                        ii = ii+1
                    if (ii > self.__nrwsx):
                        raise RuntimeError('wsinit : Error generating weights')
                            
        self.__nrws = ii-1
    
    def wsweight(self, r) :
        
        '''
            Weighting functions required to calculate dispersion relation
            
            Please check : https://www.mail-archive.com/users@lists.quantum-espresso.org/msg24388.html
            for technical details
            
            input : r - location vector in cartesian coordinate
            
            return : weight
            
        '''

        wsweight = np.float(0.0)
        nreq = 1
        for ir in range(self.__nrws):
            rrt = np.dot(r, self.__rws[1:,ir])
            ck = rrt - self.__rws[0,ir]
            if (ck > 1e-6) :
                return wsweight
            if (abs(ck) < 1e-6) : 
                nreq = nreq + 1

        wsweight = np.float32(1.0)/np.float32(nreq)

        return wsweight

    def set_asr(self, asr):
        
        '''
            Acoustic sum rule
            
            input : asr == 'simple'
            
            return : self.frc, self.zeu
        '''

        if (asr != 'simple') : raise ValueError('Sum rule not supported : set asr = simple')

        if (asr == 'simple') :
            sum = np.zeros([3,3])
            for na in range(self.nat) :
                sum = sum + self.zeu[:,:,na]

            for na in range(self.nat):
                self.zeu[:,:,na] = self.zeu[:,:,na] - np.float32(sum)/np.float32(self.nat)

            for na in range(self.nat):
                sum = np.zeros([3,3])
                for nb in range(self.nat):
                    for n1 in range(self.nr1):
                        for n2 in range(self.nr2):
                            for n3 in range(self.nr3):
                                sum = sum + self.frc[n1, n2, n3, :, :, na, nb]

                self.frc[0,0,0, :, :, na, na] = (self.frc[0,0,0, :, :, na, na]
                                                        - sum)

    def frc_blk(self, q):
        
        '''
            Calculate dynamic matrix on atom basis
            
            input : q - wavevectors in ca
            
            return : self.dyn
        '''
        
        self.__wsinit()

        if (self.__first_time) :
            self.__first_time = False
            
            self.__wscache = np.zeros([4*self.nr3 + 1,
                                       4*self.nr2 + 1,
                                       4*self.nr1 + 1, 
                                        self.nat, self.nat])

            for na in range(self.nat):
                for nb in range(self.nat):
                    for n1 in range(-2*self.nr1, 2*self.nr1+1):
                        for n2 in range(-2*self.nr2, 2*self.nr2+1):
                            for n3 in range(-2*self.nr3, 2*self.nr3+1):
                                r = np.matmul(np.array([n1,n2,n3]),self.at)
                                r_ws = r + self.tau[:,na] - self.tau[:,nb]
                                (self.__wscache[n1+2*self.nr1,
                                                n2+2*self.nr2,
                                                n3+2*self.nr3,
                                                nb, na]) = self.wsweight(r = r_ws)


        for na in range(self.nat):
            for nb in range(self.nat):
                total_weight = 0
                for n1 in range(-2*self.nr1, 2*self.nr1+1):
                    for n2 in range(-2*self.nr2, 2*self.nr2+1):
                        for n3 in range(-2*self.nr3, 2*self.nr3+1):

                            r = np.matmul(np.array([n1,n2,n3]),self.at)
                            weight = (self.__wscache[n1+2*self.nr1,
                                                     n2+2*self.nr2,
                                                     n3+2*self.nr3,
                                                     nb, na])

                            if (weight > 0) :
                                m1 = (n1+1)%self.nr1
                                if (m1<0): m1 = m1+nr1
                                m2 = (n2+1)%self.nr2
                                if (m2<0): m2 = m2+nr2
                                m3 = (n3+1)%self.nr3
                                if (m3<0): m2 = m3+nr3

                                arg = 2*np.pi*(np.dot(q, r))
                                self.dyn[:,:,na,nb] = (self.dyn[:,:,na,nb] 
                                                       + self.frc[m1-1,m2-1,m3-1,
                                                                  :,:,na,nb]*np.exp(1j*arg)*weight)
                                total_weight = total_weight + weight

                if(abs(total_weight-(self.nr1*self.nr2*self.nr3)) > 1e-6):
                    raise ValueError("Total weight is incorrect")
            
    def __dyndiag(self):
        
        '''
            Calculate dynamic matrix 
            
            return : dynamic matrix (size = [3*self.nat, 3*self.nat])
        '''
        
        dyn2 = np.zeros([3*self.nat, 3*self.nat], dtype=np.complex)

        for na in range(self.nat):
            for nb in range(self.nat):
                for ipol in range(3):
                    for jpol in range(3):
                        dyn2[(na-1)*3+ipol, (nb-1)*3+jpol] = self.dyn[ipol, jpol, na, nb]

        for na in range(self.nat):
            nta = int(self.ityp[na])
            for nb in range(self.nat):
                ntb = int(self.ityp[nb])
                for ipol in range(3):
                    for jpol in range(3):
                        dyn2[(na-1)*3+ipol, (nb-1)*3+jpol] = (dyn2[(na-1)*3+ipol, (nb-1)*3+jpol]
                                                              /(self.amass[nta]*self.amass[ntb])**(1/2))
        return dyn2

    def dispersion(self, q) :
        
        '''
            Calculate dispersion for wave-vector (q)
            
            input : q - wave-vector in cartesian coordinates 
                        q = [i, j, k] where i,j,k is between 0-1
                        q = k/(2*pi/alat) 
                        
            return : w - frequency in THz
        '''

        self.__nrwsx = 200
        self.dyn = np.zeros([3,3,self.nat,self.nat], dtype=np.complex)
        self.frc_blk(q = q)
        
        dyn2 = ph_accessories.__dyndiag()
        
        w2 = eigvals(dyn2)
        
        w = np.sqrt(np.sort(abs(w2)))
        
        return w
    
    def generate_q(self, axis, qspace):
        
        '''
            Generate a set of q points
            
            input : axis == '001'
                        equidistant points on z-axis of conventional unit cell
            
                    axis == '011'
                        equidistant points on 011 axis 
                        
                    axis == '111'
                        equidistant points on 111 axis
                        
                    axis == 'mp'
                        Monkhorst-Pack grid
                        
                    qspace : spacings between q(i+1) and q(i)
            
            return :
                    qlist = list of qpoints 
        '''
        
        if (axis == '001'):
            q = np.zeros([int(1/qspace), 3])
            for (n,i) in enumerate(np.arange(0,1,qspace)):
                q[n,:] = [0, 0, i]
        elif (axis == '011'):
            q = np.zeros([int(1/qspace), 3])
            for (n,i) in enumerate(np.arange(0,1,qspace)):
                q[n,:] = [0, i, i]
        elif (axis == '111'):
            q = np.zeros([int(1/qspace), 3])
            for (n,i) in enumerate(np.arange(0,1,qspace)):
                q[n,:] = [i, i, i]
        elif (axis == 'mp'):
            p = 0
            q = np.zeros([int(1/qspace)**3, 3])
            for i in np.arange(0,1,qspace):
                for j in np.arange(0,1,qspace):
                    for k in np.arange(0,1,qspace):
                        q[p,:] = [i,j,k]
                        p = p+1
        return q
        
    def DOS(self, qspace, wspace):
        
        '''
            Calculate DOS
            
            input : qspace - interspacings between q points
                    wspace - frequency spacings for binning
                    
            return : DOS - Density of states
                     freq - list of frquencies
                     
                     np.sum(DOS*freq) = 1
        
        '''
            
        qlist = self.generate_q('full', qspace)
        i=0
        w2 = np.zeros([qlist.shape[0], 3*self.nat])
        for row in qlist:
            q = row
            q = np.matmul(q, self.bg)
            w2[i,:] = np.sqrt(np.sort(abs(self.dispersion(q))))
            i = i+1
            
        max_freq = np.max(np.max(w2))
        
        DOS, freq = np.histogram(w2, bins=np.arange(0,max_freq,wspace), density=True)    
        
        return DOS, freq
    
    def plot(self, axis, dspace, espace):
        
        '''
            Function to generate publication quality plots
            
            input : axis == 'DOS'
                    plot DOS
                    
                    axis == '001'
                    plot dispersion along 001
                    
                    axis == '011'
                    plot dispersion along 011
                    
                    axis == '111'
                    plot dispersion along 111

        '''
        
        if (axis=='DOS') :
            hist, bins = self.DOS(dspace, espace)
        
            plt.plot(bins[:-1], hist, dspace)
        if (axis=='001') :
            qlist = self.generate_q('001', dspace)
            
            
        
    def __init__(self, File_input):
        
        '''
            Provides methods to calculate harmonic thermal properties         
            
            Input :
                File_input :- Force constant file generated using Quantum Espresso. 
                Required file format is *.fc
        '''

        (self.ntyp, self.nat, self.ityp, self.at, self.tau, self.amass, self.omega,
            self.has_zstar, self.epsil, self.zeu, self.nr1,
            self.nr2, self.nr3, self.frc) = ph_accessories.__readfc(File_input)

        self.__first_time = True
        self.recips()
        self.set_asr(asr = 'simple')