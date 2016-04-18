#!/usr/local/bin/python3

#CLS:xchudy03


import argparse
import sys
import os
import re
from lxml import etree as ET
from collections import namedtuple
from xml.dom.minidom import Document
from xml.dom import minidom
import copy

# 0 is private
# 1 is protected
# 2 is public

classes = []                #Global array of classes
conflict_flag = False       #Global flag about conflicts

#--------------------------CLASSES------------------------------------------------#
 
class ClassObject:
    #constructor
    def __init__(self, name):
        self.name = name
        self.relationships = []             #array of tuple relationship_elem
        self.complete_relations = []        #array of relationship_elem whit indirect relations
        self.relationship_elem = namedtuple('relationship_elem', 'privacy name')    #element of relationships array
        self.attributes = []                #array of tuple attribute_elem
        self.invis_attributes = []          #array of invisibility attribute_elem -> inherited as private                                              
        self.attribute_elem = namedtuple('attribute_elem', 'access type name scope from_class')     #element of attributes array
        self.methods = []                   #array of Class method
        self.invis_methods = []             #array of invisibility Methods -> inherited as private                                                    
        self.using_plan_elem = namedtuple('using_plan_elem', 'from_class name access')  #element of using entry
        self.using_plan = []                #array of using entry
        self.conflictes_elements = []       #array of conglicts elements
        self.print_XMLnode = None           #this node is using during generate XML              
        self.virtual = False                #class virtual ro not
        self.kind = "concrete"              
        self.body_class = ""                

        
    #add relationship this class whit other class
    def add_relationship(self, privacy, name):
        self.relationships.append(self.relationship_elem(privacy,name))
    #add new attribute to class
    def add_attribute(self,acc,type_,name,scope,from_class):
        self.attributes.append(self.attribute_elem(acc,type_,name, scope ,from_class))
    #add new private attribute to class
    def creat_new_private_attribute(self,acc,type_,name,scope,from_class):
        self.invis_attributes.append(self.attribute_elem(acc,type_,name, scope ,from_class))
    #delete attribute from class
    def delete_attribute(self, attribute):
        self.attributes.remove(attribute)
    #add using entry to class
    def add_using(self, fron, name, access):
        self.using_plan.append(self.using_plan_elem(fron,name, access))
    

class Method:
    #constructor
    def __init__(self,type_method, name,access):
        self.name = name
        self.type =  type_method
        self.access = access
        self.argument = namedtuple('argument', 'type name')     #atribute element
        self.arguments = []             #array of atribute alements
        self.virtual_pure = None        
        self.virtual = None
        self.scope = "instance"
        self.string_method = ""         #call method in string program use it to compare two methods
        self.from_class = ""            #whre is method defined
        self.dest_const = False         #methode is constructor or destructor
        
    #Add argument
    def add_argument(self, typeName):
        match = re.search("[&|*]",typeName)         #if its argument whit * or &
        if match == None:
            type__name = re.split("\s(?=\S+\s*$)",typeName)       #split to type and name of argument
            self.arguments.append(self.argument(type__name[0],type__name[1]))
        else:
            type_s = re.search(".+[\*\&]",typeName)
            name_s = re.search("(?<=&|\*).+",typeName)
            self.arguments.append(self.argument(type_s.group(),name_s.group()))

#Class to save conflict 
class Conflict:
    def __init__(self, name):
        self.name = name            # name of conflict member
        self.conf_members= []       # array conflict members

class UniqueStore(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if getattr(namespace, self.dest, self.default) is not None:
            parser.error(option_string + " appears several times.")
        setattr(namespace, self.dest, values)
        
#---------------------------END CLASSES------------------------------------------------#
#---------------------------DATA COLLECTION--------------------------------------------#
#Delete all redundantly chars form input
def do_normalization_of_input(input_str):
#Return array of text classes  
    input_str = re.sub('\s+',' ', input_str)        #replace sequence spaces for one space
    input_str = re.sub('[\n]+|[\r]+|[\t]+', '', input_str)          #delete enters, tabs
    input_str = re.sub('(?<=\()\s*void\s*(?=\))', '', input_str)    #delete void ass argument function exam: int foo(void){}
    arr_classes = re.split("(?:(?:;\s*)|(?:}\s*;\s*))(?=class|$)",input_str)         # cut input text to array of classes
    return arr_classes

#Delete all spacess and key words virtual and static. 
def do_normalization_of_str_method(mehod):
#Return string of method whitout spaces and key words. 
    mehod= re.sub('{', '', mehod)
    mehod= re.sub('((virtual)|(static)|\s*\=\s*0\s*$)', '', mehod)
    mehod = re.sub('[a-zA-Z_\-0-9]+\s*(?=,|\))', '', mehod)
    return mehod

#Detect and processing methods
def is_method(sample,actual_class,access):
#Return if sample was method "True" or no "False"
    const_dest = False
    match = re.search(".+(?=\s*\()",sample)             #find all before "(" if there is ( args ) function continue
    if not match == None:                               #if find is unsucess its not method
        str_StaticVirtTypeName = match.group()          #There may be keyword static, virtual, type, name
        tup_StaticTypeName__quantity = re.subn('(virtual)', '', str_StaticVirtTypeName)     #delete key word virtual if it is there. Tuple(new_str,quantity)
        tup_TypeName__quantity = re.subn('(static)', '', tup_StaticTypeName__quantity[0])   #delete key word static if it is there. Tuple(new_str,quantity)
        find_meth_Name = re.search("[a-zA-Z_\-~0-9]+(?=\s*$)",tup_TypeName__quantity[0])    #finde name
        str__Type = re.sub('[a-zA-Z_\-~0-9]+(?=\s*$)', '', tup_TypeName__quantity[0])       #delete name and residue is type
        str_Name = find_meth_Name.group()
        if is_equal(str__Type, ''):                 #if method doesn't have type its constructor or destructor
            find = re.search("~",str_Name)          #if name contains ~ its destructor and type is "void"
            if find:  
                str__Type = "void"              

            else:                                   #it is constructor
                str__Type = str_Name                
            const_dest = True
       
        new_method = Method(str__Type, str_Name, access)                #create object methode Method(type, name, privacy)
        new_method.dest_const = const_dest                              #constructor destructor flag
        new_method.from_class = actual_class.name                       #set from where is method
        new_method.string_method = do_normalization_of_str_method(sample)       #copy string of metod for comper
        if tup_TypeName__quantity[1] == 1 and tup_StaticTypeName__quantity[1] == 1:
            print("Method must not be virtual and static in one time", file=sys.stderr)
            sys.exit(4)
        if tup_TypeName__quantity[1] == 1:                              #set sope if there was "static" keyword
            new_method.scope = "static"
        if tup_StaticTypeName__quantity[1] == 1:                        #iset sope and else if there was "virtual" keyword
            new_method.virtual = True
            match = re.search("\s*=\s*0\s*$",sample)                    #if is methode defined as equal 0 is's virtual pure
            if  match == None:
                new_method.virtual_pure = "no"
            else:
                new_method.virtual_pure = "yes"
            actual_class.kind = "abstract"                              #if class have pure virtual method class is virtual to

    ##### PARSE ARGUMENTS
        match = re.search("(?<=\().+(?=\))",sample)                 #find all arguments
        if not match == None:
            str_TypesNames = match.group()
            arr_TypeName = re.split(",",str_TypesNames)             #split to array of arguments
            for TypeName in arr_TypeName:
                new_method.add_argument(TypeName)                   #Call function to add argument. Function split type and name
        if find_method(actual_class.methods,new_method.string_method) or find_attrib_class(actual_class.attributes,new_method.name):        # if method whit the same name is already in class. 
            print("In the class\""+actual_class.name+"\" already exist name of method or attribute\""+new_method.name+"\".", file=sys.stderr)
            sys.exit(4)
        actual_class.methods.append(new_method)                     #append method to class
        return True                 # it was method
    else:
        return False                # Nop it was not method

#Detect and processing attribute
def is_attribute(sample, actual_class,access):
#Return if sample was attribute "True" or no "False"
    match = re.search("\A\s*([[a-zA-Z_\-0-9,*&]+(\s+|$)){2,}(?=\=|\Z)",sample)        #chcek if is it athribute
    if not match == None:                                                   #if yes
        scope = "instance"                                                  #set default scope
        tup_TypeAth__quantity = re.subn('(static)', '',sample)              #if is metod static set it
        if tup_TypeAth__quantity[1] == 1:
            scope = "static"
        if not re.search("(virtual)",sample) == None:
            print("Virtual attribute not existing.", file=sys.stderr)
            sys.exit(4)
        match = re.search("[&|*]",tup_TypeAth__quantity[0])                 #Check chars * or & in declaration
        if match == None:                                                   #If not
            type__name = re.search("[ ]+(?=[a-zA-Z_\-0-9]+\s*(\,|\Z|\=))",tup_TypeAth__quantity[0])   #split to type and name of argument
            type_arg = tup_TypeAth__quantity[0][0:type__name.span()[0]]     #cut data type from athribute
            names_arg = tup_TypeAth__quantity[0][type__name.span()[1]:]     #cut name from athribute
        else:
            type_s = re.search(".+[\*\&]",tup_TypeAth__quantity[0])         #find type (all to * or & )
            name_s = re.search("(?<=&|\*).+",tup_TypeAth__quantity[0])      #find name (all from * or &)
            type_arg = type_s.group()
            names_arg = name_s.group()

        arr_names_arg = re.split(",",names_arg)                 #if its repeated declaration split name by comma
        for name_arg in arr_names_arg:
            if find_attrib_class(actual_class.attributes,name_arg) or find_attrib_class(actual_class.methods,name_arg):     #Chack if something is defined whit the same name
                print("In the class\""+actual_class.name+"\" already exist name of method or attribute\""+name_arg+"\".", file=sys.stderr)
                sys.exit(4)
            actual_class.add_attribute(access, type_arg, name_arg, scope, actual_class.name)       #add all finde athribute to class
        return True                 #it was athribute
    return False                    #it wan't argument

#Detect and processing access define 
def is_access_define(sample,access):
#Return actual code of access
    match = re.search("^[ ]*(private|public|protected)+[ ]*$",sample)       #its private or public or protected
    if not match == None:
        if is_equal(match.group(),"private"):
            return 0
        if is_equal(match.group(),"protected"):
            return 1
        if is_equal(match.group(),"public"):
            return 2
    return access

#Detect and processing using
def is_using(sample,actual_class,access):
#Return if sample was using "True" or no "False"
    match = re.search("\S+\s*::\s*\S+",sample)              #try find name before :: whot is sintax using
    if not match == None:
        from__name = re.split("::",match.group())
        actual_class.add_using(from__name[0],from__name[1], access)
        return True
    return False

#Create class objects , specify inheritance and split body to commands
def create_classes_and_specify_inheritance(arr_code_classes):
#Return global array of classes
    global classes
    elem = []
    for code_class in arr_code_classes:
        match = re.search("(?<=class )[a-zA-Z0-9_\-:, ]+(?={)", code_class)        #find head of class
        if not match == None:
            head_of_class = match.group().split(":",1)                      #split on two pards: Name and Inheritance
            if find_attrib_class(classes, head_of_class[0]):                #if Class is already declared it's conflict
                print("Class \""+head_of_class[0]+"\" is already defined", file=sys.stderr)
                sys.exit(4)
            new_class = ClassObject(head_of_class[0])               # Create object whit name 
            if len(head_of_class) > 1:                              # Class had inheritance
                parsed_rel = head_of_class[1].split(",")            # Cut on list of inheritances
                for inh in parsed_rel:
                    matches = re.findall("[a-zA-Z_\-0-9]+", inh)
                    if len(matches) > 1:                         #if inheritance has define privacy
                        find = find_attrib_class(new_class.relationships, matches[1])          
                        if find or matches[1] == head_of_class[0]:
                            print("Base class '"+matches[1]+"' specified more than once as a direct base class",file=sys.stderr)
                            sys.exit(4)
                        new_class.add_relationship(convert_pricacy_to_number(matches[0]), matches[1])
                    else:
                        find = find_attrib_class(new_class.relationships,  matches[0])
                        if find or  matches[0] == head_of_class[0]:
                            print("Base class '"+ matches[0]+"' specified more than once as a direct base class",file=sys.stderr)
                            sys.exit(4)
                        new_class.add_relationship(0, matches[0])
            match = re.search("(?<={)(.*|\s*)*(?=$)", code_class)       #find body
            new_class.body_class = match.group()
            classes.append(new_class)

#Function processing input and parse all data to structure
def class_procesing(input_string):
#Return golobal array of object classes
    arr_code_classes = do_normalization_of_input(input_string)
    create_classes_and_specify_inheritance(arr_code_classes)

    for class_elem in classes:
        arr_of_commands = re.split("(?<!:)[:](?!:)|;|{\s*}",class_elem.body_class)      #split body of class on comands
        access = 0
        for command in arr_of_commands:
            if command == ' ':
                continue
            if is_method(command, class_elem, access):
                continue
            if is_attribute(command, class_elem, access):
                continue
            if is_using(command, class_elem, access):
                continue
            access = is_access_define(command, access)
#---------------------------END  DATA COLLECTION--------------------------------------#
#---------------------------HELP FUNCTIONS--------------------------------------------#
def convert_pricacy_to_number(pub_prot):
    if is_equal(pub_prot,"public"):
        return 2
    if is_equal(pub_prot,"protected"):
        return 1
    return 0

def convert_number_to_privacy(priv_number):
    arr_acces = ["private", "protected", "public"]
    return arr_acces[priv_number]

def is_equal(str1,str2):
    str1 = str1.replace(' ','')
    str2 = str2.replace(' ','')
    return str1 == str2

def find_attrib_class(classes_attributes, wanted):
    for class_attr in classes_attributes:
        if is_equal(class_attr.name,wanted):
            return class_attr
    return False

def find_method(methods, wanted):
    for method in methods:
        if is_equal(method.string_method,wanted):
            return method
    return False

def finde_all_methods_whit_name(elements_whit_name, wanted):
    return_finde = []
    done = False
    for element in elements_whit_name:
        if is_equal(element.name,wanted):
            return_finde.append(element)
            done = True
    if not done:
        return []
    return return_finde

def privacy_calculator(last_access ,access):
    copy_ele = copy.copy(access)
    if last_access == 0:
        deny = True
        return copy_ele._replace(privacy=0), deny
    if copy_ele.privacy == 0:
        deny = False
        return copy_ele._replace(privacy=0), deny
    if last_access == 2 and copy_ele.privacy == 2:
        deny = False
        return copy_ele._replace(privacy=2), deny
    else:
        deny = False
        return copy_ele._replace(privacy=1), deny
#------------------------END HELP FUNCTIONS------------------------------------------#
#--------------------------DATA PROCESING--------------------------------------------#
#Process all using -> copy methods / attributes to calss
def process_using():
#Return modify  classes in global array of classes
    for class_ele in classes:
        for use_plan in class_ele.using_plan:                                       
            inh_class = find_attrib_class(classes,use_plan.from_class)              #finde class where is implement attribute / methode
            find_ele = find_attrib_class(inh_class.attributes,use_plan.name)        #Is it attribute?  
            if find_ele:
                class_ele.add_attribute(use_plan.access, find_ele.type, find_ele.name, find_ele.scope, class_ele.name)  #append attribute whit access code of using  
            else:
                arr_methodes = finde_all_methods_whit_name(inh_class.methods,use_plan.name)     #Is it methode?  
                for method_element in arr_methodes:
                    new_method = copy.copy(method_element)
                    new_method.from_class = class_ele.name
                    new_method.access = use_plan.access
                    class_ele.methods.append(new_method)            #append it

#Recursive algorithm to explore all inheritance       
def recursive_maping_inheritance(class_actual, class_base , perm_before, visited, depth_count):
#Return modify  classes in global array of classes
    depth_count += 1
    for rell in class_actual.relationships:
        if not find_attrib_class(visited, rell.name) and not is_equal(class_base.name,rell.name):   # I if newer been there and next class is not start class
                now_perm, deny = privacy_calculator(perm_before,rell)                                     #change access ecouse of access before and actual
                visited.append(now_perm)                                                            # Set ass visited
                miss_object = find_attrib_class(classes, rell.name)                                 #finde that class
                if not miss_object:
                    print("Class \""+class_base.name+"\" have relationship whit not existing class \""+rell.name+"\"", file=sys.stderr)
                    sys.exit(4)
                copy_attribute(class_base,miss_object,now_perm.privacy,deny)                   
                copy_methods(class_base,miss_object,now_perm.privacy,deny)
                recursive_maping_inheritance(miss_object,class_base,now_perm.privacy,visited,depth_count)   

#Copy methods to base class
def copy_methods(to_class,from_class, as_perm,deny):
#Return modify  classes in global array of classes
#Function is ugly because of bad assignment and subsequent patching  
    global conflict_flag
    for f_methode in from_class.methods:        # Iterating over all method in class
        if not f_methode.dest_const:    #If not constructor or destructor        #if Acces is 1 or 2 or method is virtualPURE and methode isn't hereditary 
            if (((f_methode.access == 1 or f_methode.access == 2) and not deny) or f_methode.virtual_pure == "yes" )and  is_equal(f_methode.from_class,from_class.name):    
                find = find_method(to_class.methods,f_methode.string_method)    #try find method in my method
                private_find = find_method(to_class.invis_methods,f_methode.string_method)       #try find method in my invisibility method
                if find :                   #Find in my methode
                    if not is_equal(find.from_class,to_class.name) and (f_methode.virtual == find.virtual):         #Iif one of them isn't my methode or both of isn't virtual  it is conflict
                        confilct_element = find_attrib_class(to_class.conflictes_elements,f_methode.name)
                        if confilct_element:
                            confilct_element.conf_members.append(f_methode)
                        else:
                            confilct_element= Conflict(f_methode.name)
                            confilct_element.conf_members.append(f_methode)
                            confilct_element.conf_members.append(find)
                            to_class.conflictes_elements.append(confilct_element)
                        conflict_flag = True
                elif private_find:               #Find in my invisibility  methode
                    if not is_equal(private_find.from_class,to_class.name) and (f_methode.virtual == private_find.virtual):     #Iif one of them isn't my methode or both of isn't virtual  it is conflict
                        confilct_element = find_attrib_class(to_class.conflictes_elements,f_methode.name)
                        if confilct_element:
                            confilct_element.conf_members.append(f_methode)
                        else:
                            confilct_element= Conflict(f_methode.name)
                            confilct_element.conf_members.append(f_methode)
                            confilct_element.conf_members.append(private_find)
                            to_class.conflictes_elements.append(confilct_element)
                        conflict_flag = True
                        
                else:
                    new_methode = copy.copy(f_methode)          #everything is alright append new methode
                    new_methode.access = as_perm
                    to_class.methods.append(new_methode)
            else:                                               #If i shuden't inherit -> my invisibility method
                if is_equal(f_methode.from_class,from_class.name):
                    find = find_method(to_class.methods,f_methode.string_method)
                    private_find = find_method(to_class.invis_methods,f_methode.string_method)
                    if find :
                        if not is_equal(find.from_class,to_class.name) and (f_methode.virtual == find.virtual):
                            confilct_element = find_attrib_class(to_class.conflictes_elements,f_methode.name)
                            if confilct_element:
                                confilct_element.conf_members.append(f_methode)
                            else:
                                confilct_element= Conflict(f_methode.name)
                                confilct_element.conf_members.append(f_methode)
                                confilct_element.conf_members.append(find)
                                to_class.conflictes_elements.append(confilct_element)
                            conflict_flag = True
                    elif private_find:
                        if not is_equal(private_find.from_class,to_class.name) and (f_methode.virtual == private_find.virtual):
                            confilct_element = find_attrib_class(to_class.conflictes_elements,f_methode.name)
                            if confilct_element:
                                confilct_element.conf_members.append(f_methode)
                            else:
                                confilct_element= Conflict(f_methode.name)
                                confilct_element.conf_members.append(f_methode)
                                confilct_element.conf_members.append(private_find)
                                to_class.conflictes_elements.append(confilct_element)
                            conflict_flag = True
                    else:
                        new_methode = copy.copy(f_methode)          # Everything is alright append to invisibility methods
                        new_methode.access = as_perm
                        to_class.invis_methods.append(new_methode)

#Copy attribute to base class
def copy_attribute(to_class,from_class, as_perm,deny):
#Return modify  classes in global array of classes
#Function is ugly because of bad assignment and subsequent patching
    global conflict_flag
    for f_attribute in from_class.attributes:
        if (f_attribute.access == 1 or f_attribute.access == 2) and  is_equal(f_attribute.from_class,from_class.name) and not deny:     # 

            find = find_attrib_class(to_class.attributes,f_attribute.name)
            private_find = find_attrib_class(to_class.invis_attributes,f_attribute.name)
            if find:
                
                if not is_equal(find.from_class,to_class.name):

                    confilct_element = find_attrib_class(to_class.conflictes_elements,f_attribute.name)
                    if confilct_element:
                        confilct_element.conf_members.append(f_attribute)
                    else:
                        confilct_element= Conflict(f_attribute.name)
                        confilct_element.conf_members.append(f_attribute)
                        confilct_element.conf_members.append(find)
                        to_class.conflictes_elements.append(confilct_element)
                    conflict_flag= True
            elif private_find:

                if not is_equal(private_find.from_class,to_class.name):
                    confilct_element = find_attrib_class(to_class.conflictes_elements,f_attribute.name)
                    if confilct_element:
                        confilct_element.conf_members.append(f_attribute)
                    else:
                        confilct_element= Conflict(f_attribute.name)
                        confilct_element.conf_members.append(f_attribute)
                        confilct_element.conf_members.append(private_find)
                        to_class.conflictes_elements.append(confilct_element)
                    conflict_flag= True
            else:
                to_class.add_attribute(as_perm,f_attribute.type,f_attribute.name,f_attribute.scope ,f_attribute.from_class )
        else:
            if is_equal(f_attribute.from_class,from_class.name):
                find = find_attrib_class(to_class.attributes,f_attribute.name)
                private_find = find_attrib_class(to_class.invis_attributes,f_attribute.name)
                if find:
                    if not is_equal(find.from_class,to_class.name):
                        confilct_element = find_attrib_class(to_class.conflictes_elements,f_attribute.name)
                        if confilct_element:
                            confilct_element.conf_members.append(f_attribute)
                        else:
                            confilct_element= Conflict(f_attribute.name)
                            confilct_element.conf_members.append(f_attribute)
                            confilct_element.conf_members.append(find)
                            to_class.conflictes_elements.append(confilct_element)
                        conflict_flag= True
                elif private_find:
                    if not is_equal(private_find.from_class,to_class.name):
                        confilct_element = find_attrib_class(to_class.conflictes_elements,f_attribute.name)
                        if confilct_element:
                            confilct_element.conf_members.append(f_attribute)
                        else:
                            confilct_element= Conflict(f_attribute.name)
                            confilct_element.conf_members.append(f_attribute)
                            confilct_element.conf_members.append(private_find)
                            to_class.conflictes_elements.append(confilct_element)
                        conflict_flag= True
                else:
                    to_class.creat_new_private_attribute(as_perm,f_attribute.type,f_attribute.name,f_attribute.scope ,f_attribute.from_class )

#Set using methode / attribute 
def use_using_back():
#Return modify  classes in global array of classes
    for class_ele in classes:
        for us_p in class_ele.using_plan:
            find_ele = find_attrib_class(class_ele.attributes,us_p.name)
            if find_ele:
                class_ele.add_attribute(find_ele.access,find_ele.type, find_ele.name, find_ele.scope, us_p.from_class)
                class_ele.delete_attribute(find_ele)

            else:
                arr_methodes = finde_all_methods_whit_name(class_ele.methods,us_p.name)
                for method_element in arr_methodes:
                    method_element.from_class = us_p.from_class

#Set class who have puse virtual methode as virtual              
def check_virt_methode():
#Return modify  classes in global array of classes
    for class_elem in classes:
        for meth in class_elem.methods:
            if meth.virtual_pure == "yes":
                class_elem.kind = "abstract"
            else:
                class_elem.kind = "concrete"

#Delete conflict elements from classes
def delete_conflict_method():
#Return modify  classes in global array of classes
    for class_element in classes:
        for conflict_element in class_element.conflictes_elements:
            finds = finde_all_methods_whit_name(class_element.attributes,conflict_element.name) #if find conflict element in attributes delete it
            for find in finds:                                                                      
                class_element.attributes.remove(find)
            finds = finde_all_methods_whit_name(class_element.invis_attributes,conflict_element.name) #if find conflict invis element in attributes delete it
            for find in finds:
                class_element.invis_attributes.remove(find)
            finds = finde_all_methods_whit_name(class_element.methods,conflict_element.name)    #if find conflict methods element in attributes delete it
            for find in finds:
                class_element.methods.remove(find)
            finds = finde_all_methods_whit_name(class_element.invis_methods,conflict_element.name)  #if find conflict invis methods in attributes delete it
            for find in finds:
                class_element.invis_methods.remove(find)

#Delete conflicts berween methods and attributes
def detect_conflict_between_methods_and_attributes():
#Return modify  classes in global array of classes
    global conflict_flag
    for class_element in classes:
        all_attributes = class_element.attributes + class_element.invis_attributes  
        for attribute in all_attributes:    
            arr_methods = class_element.methods + class_element.invis_methods
            arr_matches = finde_all_methods_whit_name(arr_methods,attribute.name)
            if not arr_matches == [] :
                new_conflict = Conflict(attribute.name)
                new_conflict.conf_members.append(attribute)
                conflict_flag = True
                for conflict_element in arr_matches:
                    new_conflict.conf_members.append(conflict_element)
                class_element.conflictes_elements.append(new_conflict)

#Man function of DATA Procesing part
def adding_inheritance(conflicts):
#Return modify  classes in global array of classes
    process_using()
    for class_elem in classes:
        visited = []
        recursive_maping_inheritance(class_elem, class_elem , 2, visited,0)
        class_elem.complete_relations = visited
    use_using_back()
    check_virt_methode()
    detect_conflict_between_methods_and_attributes()
    if conflict_flag and not conflicts:
        print("Conflict", file=sys.stderr)
        sys.exit(21)
    delete_conflict_method()

#-----------------------END  DATA PROCESING------------------------------------#
#-----------------------DATA PRINTING---------------------------------#
#recursive modul who create node 
def nodes_creator(actual_class,xml_code):
#Return last node
    actual_class.print_XMLnode = xml_code.createElement('class')    #create node
    actual_class.print_XMLnode.setAttribute("name", actual_class.name)
    actual_class.print_XMLnode.setAttribute("kind", actual_class.kind)
    for rell in actual_class.relationships:                         #over all relationships
        class_node_cpy = copy.copy(actual_class.print_XMLnode)      #create copy node
        next_class = find_attrib_class(classes, rell.name)          #finde next class
        if  next_class.print_XMLnode == None:                       #If i never been there
            node = print_rell_XML(next_class,xml_code)
            node.appendChild(class_node_cpy)
        else:
            next_class.print_XMLnode.appendChild(class_node_cpy)    
    return actual_class.print_XMLnode
#Function to print inheritance tree
def inheritance_tree_XML():
#xml document
    xml_code = Document()
    model = xml_code.createElement('model')
    xml_code.appendChild(model)
    for class_elem in classes:
        if class_elem.print_XMLnode == None:
            nodes_creator(class_elem,xml_code)
    for class_elem in classes:
        if len(class_elem.relationships) == 0:
            model.appendChild(class_elem.print_XMLnode)
    return xml_code

#Modul to print methodes of class
def methode_XML(xml_code, printing_class,printing_privacy,parent):
#If function append someting to xml tree
    done = False
    methods = xml_code.createElement('methods')
    for method_element in printing_class.methods:
        if method_element.access == convert_pricacy_to_number(printing_privacy):
            method = xml_code.createElement('method')
            method.setAttribute("name", method_element.name)
            method.setAttribute("type", method_element.type)
            method.setAttribute("scope", method_element.scope)
            done = True
            if not method_element.from_class == printing_class.name:
                from_elem = xml_code.createElement('from')
                from_elem.setAttribute("name", method_element.from_class)
                method.appendChild(from_elem)
            if method_element.virtual:
                virtual = xml_code.createElement('virtual')
                virtual.setAttribute("pure", method_element.virtual_pure)
                method.appendChild(virtual)
           
            arguments = xml_code.createElement('arguments')
            method.appendChild(arguments)
            for arguments_element in method_element.arguments:
                argument = xml_code.createElement('argument')
                argument.setAttribute("name", arguments_element.name)
                argument.setAttribute("type", arguments_element.type)
                arguments.appendChild(argument)
            methods.appendChild(method)
    if done:
        parent.appendChild(methods)
        return done
    return  done

#Modul to print attributes of class
def attribute_XML(xml_code, printing_class,printing_privacy,parent):
#If function append someting to xml tree
    done = False
    attributes = xml_code.createElement('attributes')
    for attribute_element in printing_class.attributes:
        if attribute_element.access == convert_pricacy_to_number(printing_privacy):  
            attribute = xml_code.createElement('attribute')
            attribute.setAttribute("name", attribute_element.name)
            attribute.setAttribute("type", attribute_element.type)
            attribute.setAttribute("scope", attribute_element.scope)
            done = True
            if not attribute_element.from_class == printing_class.name:
                from_elem = xml_code.createElement('from')
                from_elem.setAttribute("name", attribute_element.from_class)
                attribute.appendChild(from_elem)
            attributes.appendChild(attribute)
    if done:
        parent.appendChild(attributes)
        return done
    return done

#Modul to print conflicts elements if existing
def conflicts_XML(xml_code, printing_class,parent):
    if not len(printing_class.conflictes_elements) == 0:
        conflicts = xml_code.createElement('conflicts')
        parent.appendChild(conflicts)
        for conflict_element in printing_class.conflictes_elements:
            member = xml_code.createElement('member')
            member.setAttribute("name", conflict_element.name)
            conflicts.appendChild(member)
            for confict_member in conflict_element.conf_members:
                class_elem = xml_code.createElement('class')
                class_elem.setAttribute("name", confict_member.from_class)
                member.appendChild(class_elem)
                privacy = xml_code.createElement(convert_number_to_privacy(confict_member.access))
                class_elem.appendChild(privacy)
                if type(confict_member) is Method:
                    method = xml_code.createElement('method')
                    method.setAttribute("name", confict_member.name)
                    method.setAttribute("type", confict_member.type)
                    method.setAttribute("scope", confict_member.scope)
                    if confict_member.virtual:
                        virtual = xml_code.createElement('virtual')
                        virtual.setAttribute("pure", confict_member.virtual_pure)
                        method.appendChild(virtual)
                    arguments = xml_code.createElement('arguments')
                    method.appendChild(arguments)
                    for arguments_element in confict_member.arguments:
                        argument = xml_code.createElement('argument')
                        argument.setAttribute("name", arguments_element.name)
                        argument.setAttribute("type", arguments_element.type)
                        arguments.appendChild(argument)
                    privacy.appendChild(method)
                else:
                    attribute = xml_code.createElement('attribute')
                    attribute.setAttribute("name", confict_member.name)
                    attribute.setAttribute("type", confict_member.type)
                    attribute.setAttribute("scope", confict_member.scope)
                    privacy.appendChild(attribute)

#Function generate XML out 
def generate_XML(details):
#Return xml document 
    print_all_classes = False
    new_calass_found = False
    arr_acces = ["private", "protected", "public"]
    xml_code = Document()
    
    if details == '':
        print_all_classes = True
        new_calass_found = True
        mode = xml_code.createElement('model')
        xml_code.appendChild(mode)
    for printing_class in classes:
        if not print_all_classes:
            printing_class = find_attrib_class(classes, details)
            if  printing_class:
                new_calass_found = True

        if new_calass_found:
            class_base = xml_code.createElement('class')
            class_base.setAttribute("name", printing_class.name)
            class_base.setAttribute("kind", printing_class.kind)
            if print_all_classes:
                mode.appendChild(class_base)
            else:
                xml_code.appendChild(class_base)
            
            if not len(printing_class.relationships) == 0:
                inheritance = xml_code.createElement('inheritance')
                class_base.appendChild(inheritance)
            
            for relationship in printing_class.relationships:
                from_elem = xml_code.createElement('from')
                from_elem.setAttribute("name", relationship.name)
                from_elem.setAttribute("privacy", convert_number_to_privacy(relationship.privacy))
                inheritance.appendChild(from_elem)

            if conflicts and not len(printing_class.conflictes_elements) == 0: 
                conflicts_XML(xml_code, printing_class,class_base)



            for access in arr_acces:
                privacy = xml_code.createElement(access)
                done_a = attribute_XML(xml_code, printing_class,access,privacy)
                done_m = methode_XML(xml_code, printing_class,access,privacy)
                if done_a or done_m: 
                    class_base.appendChild(privacy) 
                   
        if not print_all_classes:
            break
    return xml_code

#Processing XPATH
def parseXML_XPATH(xml, xpath):
#Processing xml document
    xml = xml.toprettyxml()
    result = ET.Element("result")
    parser = ET.XMLParser(remove_blank_text=True)

    root = ET.XML(xml, parser)
    find = ET.XPath(xpath)
    TMP = "\n"
    for f in find(root):
        try:
            result.append(f)
        except:
            TMP = TMP+f+"\n"
    if len(TMP) > 1:
        result.text = TMP
    rough_string = ET.tostring(result)
    x = minidom.parseString(rough_string)
    return x
    

#-----------------------END DATA PRINTING---------------------------------------#
#--------------OPENING FILES AND ARGUMENTS PROCESS--------------------#
#Open file to read
def read_input_file(input_url):
#String of readed file
    if input_url or input_url == '':
        if not input_url == '':
            try:
                input_url = os.path.join(os.path.dirname(__file__), input_url)
                input_file = open(input_url,'r')
                return input_file.read()
            except:
                print("Problem whit open input file!", file=sys.stderr)
                sys.exit(2)
        else:
            print("Argument for input file is emty!", file=sys.stderr)
            sys.exit(1)
    return sys.stdin.read()

#Open file to write
def open_file_to_write(output_url):
#File descriptor
    if output_url or output_url == '':
        if not output_url == '':
            try:
                output_url = os.path.join(os.path.dirname(__file__), output_url)
                return open(output_url,'w')
            except:
                print("Problem whit open output file!", file=sys.stderr)
                sys.exit(3)
        else:
            print("Argument for output file is emty!", file=sys.stderr)
            sys.exit(1)
    return sys.stdout

#Parsing all argument form user
def parse_args():
#Return String of input file, file descriptor to write, pretty, details, search, conflicts 
    parser = argparse.ArgumentParser(description='Program to chcek relationships in C++ for subject IPP 2016')
    parser.add_argument("--input", action=UniqueStore, help="Imput text file")
    parser.add_argument("--output",  action=UniqueStore, help="Outpur text file in format XML")
    parser.add_argument("--pretty-xml", const=4, nargs='?',dest='pretty',action=UniqueStore,type = int, help="Count of spaces with each plunge")
    parser.add_argument("--details",const='', nargs='?',dest='details',action=UniqueStore, help="Detail informations about class")
    parser.add_argument("--search", action=UniqueStore, help="Search specify class")
    parser.add_argument("--conflicts", action='store_true' , help="Detect conflicts")

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 0:
            if len(sys.argv) == 2:
                sys.exit(0)
    
        print("Error in argument",file=sys.stderr)
        sys.exit(1)

    if (args.conflicts == True) and args.details == None:
        print("Error in argument",file=sys.stderr)
        sys.exit(1)



    #### servise of file #####
    if args.pretty == None:
        args.pretty = 4
    input_string = read_input_file(args.input)
    output_file = open_file_to_write(args.output)

    return input_string, output_file, args.pretty, args.details, args.search, args.conflicts
#--------------OPENING FILES AND ARGUMENTS PROCESS--------------------#

#-----------------START PROGRAM ---------------------

input_string, output_file, pretty, details, search, conflicts = parse_args()

##### filling data structures### 
class_procesing(input_string)   #
################################
                              
adding_inheritance(conflicts)


if details or details == '':
    xml_code = generate_XML(details)
else :
    xml_code = inheritance_tree_XML()
if search:
    xml_code = parseXML_XPATH(xml_code,search)
xml_code.writexml(output_file,""," " * pretty, "\n",encoding="UTF-8" )
