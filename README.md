# ph_accessories

ph_accessories is python module to calculate harmonic thermal properties by using DFT derived force constants. Currently support only exists for force constants derived in *.fc format using QUANTUM ESPRESSO.

## Usage

ph_accessories(File_input)

			Provides methods to calculate harmonic thermal properties         
            
            Input :
                File_input :- Force constant file generated using Quantum Espresso. 
                Required file format is *.fc

This example shows how to calculate density of states for Si using the force constant file 'Si_q2.fc'

```python

from ph_accessories import ph_accessories as ph

Si = ph('Si_q2.fc')

# Returns the density of states for Si, using a Mokhorst Pack grid with 0.1 q spacing and generated with frequency spacing of 1 THz
DOS, freq = Si.DOS(qspace = 0.1, wspace = 1e12) 

```

## Material variables

ph.ntyp 	--> Number of type of atoms in the unit cell (int)
ph.nat 		--> Number of atoms in the unit cell (int)
ph.ityp 	--> Array of size ph.nat, where ityp[na] is integer defining the type of atom
ph.at   	--> lattice vectors of the unit cell
ph.tau  	--> basis  vectors of the unit cell
ph.amass 	--> mass of every atom in the unit cell. Array of size ph.ntyp
ph.omega 	--> Volume of unit cell
ph.epsil 	--> dielectric matrix
ph.frc  	--> Force constant tensor.
ph.bg 		--> Reciprocal lattice vectors

## Function Calls

ph.recips() 	

			Calculate reciprocal lattice vectors
			return : ph.bg

ph.wsweight(r) 	

            Weighting functions required to calculate dispersion relation
            
            Please check : https://www.mail-archive.com/users@lists.quantum-espresso.org/msg24388.html
            for technical details
            
            input : r - location vector in cartesian coordinate
            
            return : weight

ph.set_ast(asr)

			Acoustic sum rule
            
            input : asr == 'simple'
            
            return : self.frc, self.zeu

 ph.frc_blk(q)

 			Calculate dynamic matrix on atom basis
            
            input : q - wavevectors in ca
            
            return : self.dyn

ph.generate_q(axis, qspace)

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

ph.DOS(qspace, wspace)

			Calculate DOS
            
            input : qspace - interspacings between q points
                    wspace - frequency spacings for binning
                    
            return : DOS - Density of states
                     freq - list of frquencies
                     
                     np.sum(DOS*freq) = 1

ph.plot(axis, dspace, espace)

			Function to generate publication quality plots
            
            input : axis == 'DOS'
                    plot DOS
                    
                    axis == '001'
                    plot dispersion along 001
                    
                    axis == '011'
                    plot dispersion along 011
                    
                    axis == '111'
                    plot dispersion along 111

