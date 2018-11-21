# Importing helper class for setting up a reachability planning problem
from hpp.corbaserver.rbprm.rbprmbuilder import Builder

# Importing Gepetto viewer helper class
from hpp.gepetto import Viewer

rootJointType = 'freeflyer'
packageName = 'hpp-rbprm-corba'
meshPackageName = 'hpp-rbprm-corba'
# URDF file describing the trunk of the robot HyQ
urdfName = 'anymal_all'
# URDF files describing the reachable workspace of each limb of HyQ
urdfNameRom = ['anymal_lhleg_rom','anymal_lfleg_rom','anymal_rfleg_rom','anymal_rhleg_rom']
urdfSuffix = ""
srdfSuffix = ""

# Creating an instance of the helper class, and loading the robot
rbprmBuilder = Builder ()
rbprmBuilder.loadModel(urdfName, urdfNameRom, rootJointType, meshPackageName, packageName, urdfSuffix, srdfSuffix)
rbprmBuilder.setJointBounds ("base_joint_xyz", [-3,5, -1, 1, 0.3, 4])  #[-2,5, -1, 1, 0.3, 4]) 
# The following lines set constraint on the valid configurations:
# a configuration is valid only if all limbs can create a contact ...
rbprmBuilder.setFilter(['anymal_rhleg_rom', 'anymal_lfleg_rom', 'anymal_rfleg_rom','anymal_lhleg_rom'])
rbprmBuilder.setAffordanceFilter('anymal_rhleg_rom', ['Support'])
rbprmBuilder.setAffordanceFilter('anymal_rfleg_rom', ['Support',])
rbprmBuilder.setAffordanceFilter('anymal_lhleg_rom', ['Support'])
rbprmBuilder.setAffordanceFilter('anymal_lfleg_rom', ['Support',])
# We also bound the rotations of the torso.
rbprmBuilder.boundSO3([-0.4,0.4,-0.4,0.4,-0.4,0.4]) #original [-0.4,0.4,-3,3,-3,3]

# Creating an instance of HPP problem solver and the viewer
from hpp.corbaserver.rbprm.problem_solver import ProblemSolver
ps = ProblemSolver( rbprmBuilder )
r = Viewer (ps)

# Setting initial and goal configurations
q_init = rbprmBuilder.getCurrentConfig ();
q_init [0:3] = [-2.5, 0, 0.49]; rbprmBuilder.setCurrentConfig (q_init); r (q_init)
q_goal = q_init [::]
q_goal [0:3] = [2, 0, 0.48]; r (q_goal) #[3, 0, 0.5]

# Choosing a path optimizer
ps.addPathOptimizer("RandomShortcut")
ps.setInitialConfig (q_init)
ps.addGoalConfig (q_goal)

from hpp.corbaserver.affordance.affordance import AffordanceTool
afftool = AffordanceTool ()
afftool.loadObstacleModel (packageName, "darpa", "planning", r, reduceSizes=[0.05,0.,0.])
#~ afftool.visualiseAffordances('Support', r, [0.25, 0.5, 0.5])

# Choosing RBPRM shooter and path validation methods.
# Note that the standard RRT algorithm is used.
ps.client.problem.selectConFigurationShooter("RbprmShooter")
ps.client.problem.selectPathValidation("RbprmPathValidation",0.05)

# Solve the problem
t = ps.solve ()
if isinstance(t, list):
	t = t[0]* 3600000 + t[1] * 60000 + t[2] * 1000 + t[3]	

# Playing the computed path
from hpp.gepetto import PathPlayer
pp = PathPlayer (rbprmBuilder.client.basic, r)

q_far = q_init [::]
q_far [0:3] = [-2, -3, 0.63]; 
r(q_far)

for i in range(1,10):
	rbprmBuilder.client.basic.problem.optimizePath(i)
	

from hpp.corbaserver import Client
from hpp.corbaserver.robot import Robot as Parent

class Robot (Parent):
	rootJointType = 'freeflyer'
	packageName = 'hpp-rbprm-corba'
	meshPackageName = 'hpp-rbprm-corba'
	# URDF file describing the trunk of the robot HyQ
	urdfName = 'anymal_all'
	urdfSuffix = ""
	srdfSuffix = ""
	def __init__ (self, robotName, load = True):
		Parent.__init__ (self, robotName, self.rootJointType, load)
		self.tf_root = "base_footprint"
		self.client.basic = Client ()
		self.load = load
		
 #DEMO code to play root path and final contact plan
cl = Client()
cl.problem.selectProblem("rbprm_path")
rbprmBuilder2 = Robot ("toto")
ps2 = ProblemSolver( rbprmBuilder2 )
cl.problem.selectProblem("default")
cl.problem.movePathToProblem(3,"rbprm_path",rbprmBuilder.getAllJointNames())
r2 = Viewer (ps2, viewerClient=r.client)
r2(q_far)
