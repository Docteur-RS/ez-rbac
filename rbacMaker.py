from string import Template
from subprocess import call

KUBECTL_PATH = "usr/local/bin/kubectl"
MENU_BANNER = "\n######## ########         ########  ########     ###     ######\n##            ##          ##     ## ##     ##   ## ##   ##    ##\n##           ##           ##     ## ##     ##  ##   ##  ##       \n######      ##    ####### ########  ########  ##     ## ##       \n##         ##             ##   ##   ##     ## ######### ##       \n##        ##              ##    ##  ##     ## ##     ## ##    ## \n######## ########         ##     ## ########  ##     ##  ###### \n"

class Store(object):
    def __init__(self):
        self.serviceAccount = False
        self.ns = []
        self.role = []
        self.roleBinding = []

class Kubectl(object):

    def createNs(self, nsName):
        print("create NS" + nsName)
        call(["kubectl", "create", "ns", nsName])

    def printNs(self):
        print("print NS")
        call(["kubectl", "get", "ns"])

    def createSa(self, saName):
        call(["kubectl", "create", "sa", saName])

    def printSa(self):
        call(["kubectl", "get", "sa"])

    def printSecrets(self):
        call(["kubectl", "get", "secrets"])

    def printSaToken(self, secretName):
        call(["kubectl", "describe", "secret", secretName])

    def printConfig(self):
        call(["kubectl", "config", "view"])
        
    def printCredentialToken(self, credentialName):
        call(["kubectl", "config view -o jsonpath='{.users[?(@.name == '" + credentialName + "')].user.token'"]) #kubectl config view -o jsonpath='{.users[?(@.name == "sa-with-token")].user.token}'

    def createFromFile(self, path):
        call(["kubectl", "create", "-f", path])

    def createCluster(self, remoteName, remoteIp):
        #print("kubectl config set-cluster secureRemote --server=https://127.0.0.1:6443")
        call(["kubectl", "config", "set-cluster", remoteName, "--server", remoteIp])

    def createCredentials(self, credentialName, token):
        call(["kubectl", "config", "set-credentials", credentialName, "--token", token])

    def createContext(self, contextName, credentialsName, remoteName):
        #kubectl config set-context context-api-explorer --cluster=secureRemote --user=user-api-explorer
        call(["kubectl", "config", "set-context", contextName, "--cluster", remoteName, "--user", credentialsName])

    def useContext(self, contextName):
        #k config use-context context-api-explorer
        call(["kubectl", "use-context", contextName])

              
class FileMngr(object):

    def __init__(self):
        fileData = "";

    def read(self, path):
        with open(path, 'r') as myfile:
            return myfile.read()

    def write(self, path, data):
        with open(path,'w',encoding = 'utf-8') as f:
            f.write(data)
            

class Question(object):
    
    def askYesNo(self, question):
        answer = input(question + " [Y/N]\n$ ")
        if answer == "y" or answer == "yes":
            return "yes"
        elif answer == "n" or answer == "no":
            return "no"
        else:
            print("Please enter yes or no.")
            return self.askYesNo(question)

    def ask(self, question):
        question = question + "\n$ "
        return input(question)

    def askInSelection(self, question, answers):
        question = question + "\n$ "
        userAnswer = input(question)
        if userAnswer in answers:
            return userAnswer
        else:
            print("Please answer using : ")
            print(*answers)
            self.askInSelection(question, answers);


class SessionMngr(object):

    def __init__(self):
        self.remoteIp = "127.0.0.1"
        self.remoteName = ""
        self.credentialName = ""
        self.secret = ""
        self.token = ""
        self.contextName = ""

    def createCluster(self):
        if question.askInSelection("Create new OR use existing cluster ? create(c), use(u)", ["c", "u"]) == "c":
            self.remoteIp = "https://" + question.ask("Ip of remote cluster = https://")
        else:
            kubectl.printConfig()
            print("Displayed existing clusters...")
        self.remoteName = question.ask("Enter the cluster name that you want to use :")
        kubectl.createCluster(self.remoteName, self.remoteIp)

    def createCredentials(self):
        if question.askInSelection("Create new OR use existing credentials ? create(c), use(u)", ["c", "u"]) == "c":
            sa = rbac.askServiceAccount()
            kubectl.printSecrets()
            self.secret = question.ask("Please copy paste associated secret :")
            kubectl.printSaToken(self.secret)
            self.token = question.ask("Please copy paste associated token")
            self.credentialName = question.ask("Enter new credential name :")
            kubectl.createCredentials(self.credentialName, self.token)
        else:
            kubectl.printConfig()
            self.credentialName = question.ask("Enter the credential name that you want to use :")
            kubectl.printCredentialToken(self.credentialName)       

    def createContext(self):
        if question.askInSelection("Create new OR use existing context ? create(c), use(u)", ["c", "u"]) == "c":
            self.contextName = question.ask("Name of the new context :")
        else:
            self.useContext()
            return
        if self.credentialName == "":
            self.createCredentials()
        if self.remoteName == "":
            self.createCluster()
        kubectl.createContext(self.contextName, self.credentialName, self.remoteName);

    def useContext(self):
        kubectl.printConfig()
        print("Displayed existing contexts...")
        self.contextName = question.ask("Enter the context name that you want to use :")
        kubectl.useContext(self.contextname)
        

class Rbac(object):

    def askServiceAccount(self):
        answer = question.askInSelection("create new OR use existing service account ? create(c), use(u)", ["c", "u"])
        if answer == "c":
            sa = question.ask("Name of new service account :")
            kubectl.createSa(sa);
        elif answer == "u":
            kubectl.printSa();
            sa = question.ask("Above is displayed the list of current service account(s). Please choose one and type it :")
        store.serviceAccount = sa
        return sa

    #Pe etre besoin de boucle inf pour en demander plusieurs...
    def createOrUseNs(self):
        answer = question.askInSelection("create new OR use existing namespace ? create(c), use(u)  | 'cancel' to cancel", ["c", "u", "cancel"])
        if answer == "c":
            nsName = question.ask("Name of new namespace :")
            kubectl.createNs(nsName)
            finalChoices.ns.append(nsName)
        elif answer == "u":
            kubectl.printNs()
            nsName = question.ask("Namespace to secure :")
            finalChoices.ns.append(nsName)
        else:
            return

    def createRole(self, isTypeCluster = False):
        roleNamespace = ""
        roleName = question.ask("Name :")
        if isTypeCluster == False:
            roleNamespace = question.ask("Namespace :")
        roleRessources = question.ask("Ressources of role (ex 'pods', 'deployments') :")
        roleVerbs = question.ask("Verbs of role (ex 'get', 'watch', 'list') :")
        fileData = fileMngr.read("./" + helper.getRoleType(isTypeCluster) +".yaml")
        #print(fileData)
        template = Template(fileData);
        filled = template.substitute(roleName=roleName, roleNamespace=roleNamespace, roleRessources=roleRessources, roleVerbs=roleVerbs);
        store.role.append(filled)
        print("Final file = \n\n" + filled);
        if question.askYesNo("Write file ?") == "yes":
            path = question.ask("File name to write :")
            fileMngr.write(path, filled)
        if question.askYesNo("Apply file ?") == "yes":
            kubectl.createFromFile(path)
                
    def createRoleBinding(self, isTypeCluster = False):
        roleBindingNamespace = ""
        roleBindingName = question.ask("Name :")
        if isTypeCluster == False:
            roleBindingNamespace = question.ask("Namespace :")
            roleBindingRoleType = "ClusterRole"
        else:
            roleBindingRoleType = question.ask("Type of role to bind role or clusterRole (Role, ClusteRole) :")
        roleBindingRoleName = question.ask("Role name to bind :")
        roleBindingSubjectName = question.ask("Subject name to bind :")
        roleBindingSubjectNamespace = question.ask("Subject namespace :")
        fileData = fileMngr.read("./" + helper.getRoleBindingType(isTypeCluster) +".yaml");
        #print(fileData)
        template = Template(fileData);
        filled = template.substitute(roleBindingName=roleBindingName, roleBindingNamespace=roleBindingNamespace, roleBindingRoleType=roleBindingRoleType, roleBindingRoleName=roleBindingRoleName, roleBindingSubjectName=roleBindingSubjectName, roleBindingSubjectNamespace=roleBindingSubjectNamespace);
        store.roleBinding.append(filled)
        print("Final file = \n\n" + filled);
        if question.askYesNo("Write file ?") == "yes":
            path = question.ask("File name to write : :")
            fileMngr.write(path, filled)
        if question.askYesNo("Apply file ?") == "yes":
            kubectl.createFromFile(path)

class Helper(object):

    def getRoleBindingType(self, isTypeCluster):
        return "ClusterRoleBinding" if isTypeCluster == True else "RoleBinding" #mettre des constantes !
    def getRoleType(self, isTypeCluster):
        return "ClusterRole" if isTypeCluster == True else "Role"


class Menu(object):
    
    def __init__(self):
        print(MENU_BANNER)
        answer = question.askInSelection("What can I do for you ?\n\nCreate role ? (r)\nCreate cluster role ? (cr)\nCreate role binding ? (rb)\nCreate Cluster role binding ? (crb)\n\nCreate context ? (cc)\nUse context ? (uc)", ["r", "rb", "cr", "crb", "cc", "uc"])
        if answer == "r":
            rbac.createRole()
        elif answer == "rb":
            rbac.createRoleBinding()
        elif answer == "cr":
            rbac.createRole(True)#
        elif answer == "crb":
            rbac.createRoleBinding(True)#
        elif answer == "cc":
            sessionMngr.createContext()
        elif answer == "uc":
            sessionMngr.useContext();
            


helper = Helper()
question = Question()
store = Store()
kubectl = Kubectl();
fileMngr = FileMngr();
rbac = Rbac()
sessionMngr = SessionMngr()
menu = Menu()

#sessionMngr.createContext()

#main.createRoleBinding()
#main.askServiceAccount()
#main.createOrUseNs()








