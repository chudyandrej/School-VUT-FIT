import argparse
import sys
import os
import re
from lxml import etree as ET
from collections import namedtuple
from xml.dom.minidom import Document
import copy


# 0 is private
# 1 is protected
# 2 is public

classes = []

##############################   DEFINE CLASSES TO STORE DATA

class ClassesObject:
    #constructor
    def __init__(self, name):
        self.name = name
        self.relationships = []                                                    #array of tuple relationship_elem
        self.complete_relations = []
        self.relationship_elem = namedtuple('relationship_elem', 'privacy name')    #element of relationships array
        self.attributes = []                                                #array of tuple attribute_elem
        self.attribute_elem = namedtuple('attribute_elem', 'access type name scope from_class')     #element of attributes array
        self.methods = []                                                   #array of methods
        self.using_plan_elem = namedtuple('using_plan_elem', 'from_class name access')
        self.using_plan = []
        self.print_node = None
        self.virtual = False
        self.kind = "concrete"
        self.body_class = ""
    # add relationship of this clas whit other class
    def add_relationship(self, privacy, name):
        self.relationships.append(self.relationship_elem(privacy,name))

    def add_attribute(self,acc,type_,name,scope,from_class):
        self.attributes.append(self.attribute_elem(acc,type_,name, scope ,from_class))
    def delete_attribute(self, attribute):
        self.attributes.remove(attribute)
    def add_using(self, fron, name, access):
        self.using_plan.append(self.using_plan_elem(fron,name, access))

    def creat_new_attribute(self,acc,type_,name,scope,from_class):
        self.attributes.append(self.attribute_elem(acc,type_,name, scope ,from_class))

class Method:
    def __init__(self,type_method, name,access):
        self.name = name
        self.type =  type_method
        self.access = access
        self.arguments = []
        self.argument = namedtuple('argument', 'type name')
        self.virtual_pure = None
        self.virtual = None
        self.is_defined = False
        self.scope = "instance"
        self.string_method = ""
        self.from_class = ""

    def add_argument(self, typeName):
        match = re.search("[&|*]",typeName)
        if match == None:
            type__name = re.split("\s(?=\S+\s*$)",typeName)       #split to type and name of argument
            self.arguments.append(self.argument(type__name[0],type__name[1]))
        else:
            type_s = re.search(".+[\*\&]",typeName)
            name_s = re.search("(?<=&|\*).+",typeName)
            self.arguments.append(self.argument(type_s.group(),name_s.group()))

########   PARSE INPUT CODE AND STORE TO OBJECTS

def is_method(sample,actual_class,access):
    ##### PARSE INFORMATION ABOUT METHOD
    match = re.search(".+(?=\s*\()",sample)             #find all before "(" if there is ( args ) function continue
    if not match == None:                               #if find is unsucess its not method
        str_StaticVirtTypeName = match.group()          #There may be keyword static, virtual, type, name
        tup_StaticTypeName__quantity = re.subn('(virtual)', '', str_StaticVirtTypeName)  #delete key word virtual if it is there. Tuple(new_str,quantity)
        tup_TypeName__quantity = re.subn('(static)', '', tup_StaticTypeName__quantity[0])  #delete key word static if it is there. Tuple(new_str,quantity)
        list_Type__Name = re.split("\s(?=\S+\s*$)",tup_TypeName__quantity[0])       #split type and name
        new_method = Method(list_Type__Name[0], list_Type__Name[1], access)         #create object methode Method(type, name, privacy)
        new_method.from_class = actual_class.name                       #set from where is method
        new_method.string_method = sample                               #copy string of metod for comper
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
        actual_class.methods.append(new_method)                     #append method to class
        return True                 # it was method
    else:
        return False                # Nop it was not method

#parse athribute
def is_athribute(sample, actual_class,access):
    match = re.search("\A\s*([a-zA-Z_,*&]+(\s+|$)){2,}(?=\=|\Z)",sample)        #chcek if is it athribute
    if not match == None:                                                   #if yes
        scope = "instance"                                                  #set default scope
        tup_TypeAth__quantity = re.subn('(static)', '',sample)              #if is metod static set it
        if tup_TypeAth__quantity[1] == 1:
            scope = "static"
        match = re.search("[&|*]",tup_TypeAth__quantity[0])                 #Check chars * or & in declaration
        if match == None:                                                   #If not
            type__name = re.search("[ ]+(?=[a-zA-Z_]+\s*(\,|\Z|\=))",tup_TypeAth__quantity[0])   #split to type and name of argument
            type_arg = tup_TypeAth__quantity[0][0:type__name.span()[0]]     #cut data type from athribute
            names_arg = tup_TypeAth__quantity[0][type__name.span()[1]:]     #cut name from athribute
        else:
            type_s = re.search(".+[\*\&]",tup_TypeAth__quantity[0])         #find type (all to * or & )
            name_s = re.search("(?<=&|\*).+",tup_TypeAth__quantity[0])      #find name (all from * or &)
            type_arg = type_s.group()
            names_arg = name_s.group()

        arr_names_arg = re.split(",",names_arg)                 #if its repeated declaration split name by comma
        for name_arg in arr_names_arg:
            if find_attrib_class(actual_class.attributes,name_arg):
                print("Attribute whit name \""+name_arg+"\" is already defined", file=sys.stderr)
                sys.exit(1)
            actual_class.add_attribute(access, type_arg, name_arg, scope, actual_class.name)       #add all finde athribute to class
        return True                 #it was athribute
    return False                    #it wan't argument

#change access in class
def is_access_define(sample,access):
    match = re.search("^[ ]*(private|public|protected)+[ ]*$",sample)       #its private or public or protected
    if not match == None:
        if is_equal(match.group(),"private"):
            return 0
        if is_equal(match.group(),"protected"):
            return 1
        if is_equal(match.group(),"public"):
            return 2
    return access

def is_using(sample,actual_class,access):
    match = re.search("\S+\s*::\s*\S+",sample)              #try find name before :: whot is sintax using
    if not match == None:
        from__name = re.split("::",match.group())

        actual_class.add_using(from__name[0],from__name[1], access)
        return True
    return False

def parse_body_classes():
    for class_elem in classes:
        arr_of_commands = re.split("(?<!:)[:](?!:)|;|{\s*}",class_elem.body_class)      #split body of class on comands
        access = 0
        for command in arr_of_commands:
            if command == ' ':
                continue
            if is_method(command, class_elem, access):
                continue
            if is_athribute(command, class_elem, access):
                continue
            if is_using(command, class_elem, access):
                continue
            access = is_access_define(command, access)

def create_classes_and_rel(arr_code_classes):
    global classes
    elem = []
    for code_class in arr_code_classes:
        match = re.search("(?<=class ).*(?={)", code_class)        #find head of class
        if not match == None:
            head_of_class = match.group().split(":",1)
            if find_attrib_class(classes, head_of_class[0]):
                print("Class \""+head_of_class[0]+"\" is already defined", file=sys.stderr)
                sys.exit(1)
            new_class = ClassesObject(head_of_class[0])
            if len(head_of_class) > 1:                              # class had inheritance
                parsed_rel = head_of_class[1].split(",")            # cut on list of inheritances
                for inh in parsed_rel:
                    matches = re.findall("[a-zA-Z_]+", inh)
                    if len(matches) > 1:
                        new_class.add_relationship(convert_pub_prot(matches[0]), matches[1])
                    else:
                        new_class.add_relationship(0, matches[0])
            match = re.search("(?<={)(.*|\s*)*(?=$)", code_class)       #find body
            new_class.body_class = match.group()
            classes.append(new_class)

############ HELP MINI function
#find attribute or class in array of attributes or classes
def find_attrib_class(classes_attributes, wanted):
    for class_attr in classes_attributes:
        if is_equal(class_attr.name,wanted):
            return class_attr
    return False
#find method in array of methods
def find_method(methods, wanted):
    for method in methods:
        method.string_method = re.sub('((virtual)|\s*\=\s*0\s*$)', '', method.string_method)
        wanted= re.sub('((virtual)|\s*\=\s*0\s*$)', '', wanted)
        if is_equal(method.string_method,wanted):
            return method
    return False
########### if equal 2 strings whitout white spaces
def is_equal(str1,str2):
    str1 = str1.replace(' ','')
    str2 = str2.replace(' ','')
    return str1 == str2
#########relationship conflicts###############
def use_using():
    for class_ele in classes:

        for us_p in class_ele.using_plan:
            inh_class = find_attrib_class(classes,us_p.from_class)
            find_ele = find_attrib_class(inh_class.attributes,us_p.name)
            if find_ele:
                class_ele.add_attribute(us_p.access, find_ele.type, find_ele.name, find_ele.scope, class_ele.name)
            else:
                find_ele = copy.copy(find_attrib_class(inh_class.methods,us_p.name))
                find_ele.from_class = class_ele.name
                find_ele.access = us_p.access
                inh_class.methods.append(find_ele)


def adding_inheritance():
    use_using()
    for class_elem in classes:
        visited = []
        map_rell(class_elem, class_elem , 2, visited,0)
        class_elem.complete_relations = visited;
    use_using_back()
    check_virt_methode()

def map_rell(class_actual, class_base , perm_before, visited, depth_count):
    depth_count += 1
    for rell in class_actual.relationships:
        if not find_attrib_class(visited, rell.name) and not is_equal(class_base.name,rell.name):   #I if newer been there and next class is not start class
                now_perm, deny = change_acces(perm_before,rell)                       #change access ecouse of access before and actual
                visited.append(now_perm)                                        # Set ass visited
                miss_object = find_attrib_class(classes, rell.name)             #finde that class
                if not miss_object:
                    print("Class \""+obj.name+"\" have relationship whit not existing class \""+rell.name+"\"", file=sys.stderr)
                    sys.exit(1)
                copy_attribute(class_base,miss_object,now_perm.privacy,deny)
                copy_methods(class_base,miss_object,now_perm.privacy,deny)
                map_rell(miss_object,class_base,now_perm.privacy,visited,depth_count)
        continue

def change_acces(last_access ,access):
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

def convert_pub_prot(pub_prot):
    if is_equal(pub_prot,"public"):
        return 2
    if is_equal(pub_prot,"protected"):
        return 1
    return 0

def copy_methods(to_class,from_class, as_perm,deny):
    for f_methode in from_class.methods:
        if (((f_methode.access == 1 or f_methode.access == 2) and not deny) or f_methode.virtual_pure == "yes" )and  is_equal(f_methode.from_class,from_class.name):
            find = find_method(to_class.methods,f_methode.string_method)
            if find:
                if not is_equal(find.from_class,to_class.name) and (f_methode.virtual == find.virtual):
                    print("Conflict class \""+to_class.name+"\" inherits the same name method from different classes \""+find.from_class+"\""" and "+f_methode.from_class, file=sys.stderr)
                    sys.exit(21)
            else:

                new_methode = copy.copy(f_methode)
                new_methode.access = as_perm
                to_class.methods.append(new_methode)
##############################################

def copy_attribute(to_class,from_class, as_perm,deny):
    for f_attribute in from_class.attributes:
        if (f_attribute.access == 1 or f_attribute.access == 2) and  is_equal(f_attribute.from_class,from_class.name) and not deny:
            find = find_attrib_class(to_class.attributes,f_attribute.name)
            if find:
                if not is_equal(find.from_class,to_class.name):
                    print("Conflict class \""+to_class.name+"\" inherits the same name attributes from different classes \""+find.from_class+"\""" and "+f_attribute.from_class, file=sys.stderr)
                    sys.exit(21)
            else:
                to_class.creat_new_attribute(as_perm,f_attribute.type,f_attribute.name,f_attribute.scope ,f_attribute.from_class )

def use_using_back():
    for class_ele in classes:
        for us_p in class_ele.using_plan:
            find_ele = find_attrib_class(class_ele.attributes,us_p.name)
            if find_ele:
                class_ele.add_attribute(find_ele.access,find_ele.type, find_ele.name, find_ele.scope, us_p.from_class)
                class_ele.delete_attribute(find_ele)

            else:
                find_ele = find_attrib_class(class_ele.methods,us_p.name)
                find_ele.from_class = us_p.from_class

def check_virt_methode():
    for class_elem in classes:
        for meth in class_elem.methods:
            if meth.virtual_pure == "yes":
                class_elem.kind = "abstract"
            else:
                class_elem.kind = "concrete"
##############################################
def relationship_XML(output_file):
    xml_code = Document()
    model = xml_code.createElement('model')
    xml_code.appendChild(model)
    for class_elem in classes:
        if class_elem.print_node == None:
            print_rell_XML(class_elem,xml_code)

    for class_elem in classes:
        if len(class_elem.relationships) == 0:
            model.appendChild(class_elem.print_node)
    return xml_code

def print_rell_XML(actual_class,xml_code):
    actual_class.print_node = xml_code.createElement('class')
    actual_class.print_node.setAttribute("name", actual_class.name)
    actual_class.print_node.setAttribute("kind", actual_class.kind)
    for rell in actual_class.relationships:
        class_node_cpy = copy.copy(actual_class.print_node)
        next_class = find_attrib_class(classes, rell.name)
        if  next_class.print_node == None:
            node = print_rell_XML(next_class,xml_code)
            node.appendChild(class_node_cpy)
        else:
            next_class.print_node.appendChild(class_node_cpy)
    return actual_class.print_node

def generate_XML(details, output_file):
    arr_acces = ["private", "protected", "public"]
    xml_code = Document()
    print_all = False
    continue_print = False
    if details == '':
        print_all = True
        continue_print = True
        mode = xml_code.createElement('model')
        xml_code.appendChild(mode)

    for cc in classes:
        count = 0
        pre_c_att = True
        per_c_met = True
        inh_uck = True
        use_using = False
        if not print_all:
            cc = find_attrib_class(classes, details)
            if  cc:
                continue_print = True;
        if continue_print:
            class_base = xml_code.createElement('class')
            class_base.setAttribute("name", cc.name)
            class_base.setAttribute("kind", cc.kind)
            if print_all:
                mode.appendChild(class_base)
            else:
                xml_code.appendChild(class_base)

            for inh in cc.relationships:
                if inh_uck:
                    inheritance = xml_code.createElement('inheritance')
                    class_base.appendChild(inheritance)
                    inh_uck = False
                inh_from = xml_code.createElement('from')
                inh_from.setAttribute("name", inh.name)
                inh_from.setAttribute("privacy", arr_acces[inh.privacy])
                inheritance.appendChild(inh_from)

            count = 0;
            for acces in arr_acces:
                pri_prot_publ = xml_code.createElement(acces)

                for attribute in cc.attributes:
                    if attribute.access == count:
                        if pre_c_att:
                            use_using = True;
                            print_attributes = xml_code.createElement('attributes')
                            pri_prot_publ.appendChild(print_attributes)
                            pre_c_att = False
                        if not len(attribute) == 0:
                            attr = xml_code.createElement('attribute')
                            attr.setAttribute("name", attribute.name)
                            attr.setAttribute("type", attribute.type)
                            attr.setAttribute("scope", attribute.scope)
                        if not attribute.from_class == cc.name:
                            prt_from = xml_code.createElement('from')
                            prt_from.setAttribute("name", attribute.from_class)
                            attr.appendChild(prt_from)
                        print_attributes.appendChild(attr)

                for methode in cc.methods:
                    if methode.access == count:
                        if per_c_met:
                            print_methodes = xml_code.createElement('methods')
                            pri_prot_publ.appendChild(print_methodes)
                            per_c_met = False
                        use_using = True;
                        meth = xml_code.createElement('method')
                        meth.setAttribute("name", methode.name)
                        meth.setAttribute("type", methode.type)
                        meth.setAttribute("scope", methode.scope)
                        if  not methode.from_class == cc.name:
                            prt_from = xml_code.createElement('from')
                            prt_from.setAttribute("name", methode.from_class)
                            meth.appendChild(prt_from)
                        if methode.virtual:
                            virtual_prt = xml_code.createElement('virtual')
                            virtual_prt.setAttribute("pure", methode.virtual_pure)
                            meth.appendChild(virtual_prt)
                        print_methodes.appendChild(meth)
                        arguments_print = xml_code.createElement('arguments')
                        meth.appendChild(arguments_print)
                        for argm in methode.arguments:
                            argument_print = xml_code.createElement('argument')
                            argument_print.setAttribute("name", argm.name)
                            argument_print.setAttribute("type", argm.type)
                            arguments_print.appendChild(argument_print)
                if use_using:
                    class_base.appendChild(pri_prot_publ)
                count +=1
                per_c_met = True
                pre_c_att = True
                use_using = False
            if not print_all:
                break
    return xml_code


def parseXML_XPATH(xml, xpath):
    xml = xml.toprettyxml()
    doc = Document()
    result = doc.createElement("result")
    doc.appendChild(result)

    root = ET.XML(xml)
    find = ET.XPath(xpath)

    for f in find(root):
        result.appendChild(Document().createTextNode(f))
    return doc

def read_input_file(input_url):
    if input_url :
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

def open_file_to_write(output_url):
    if output_url :
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


def parse_args():
    parser = argparse.ArgumentParser(description='Program to chcek relationships in C++ for subject IPP 2016')
    parser.add_argument("--input", help="Imput text file")
    parser.add_argument("--output",  help="Outpur text file in format XML")
    parser.add_argument("--pretty-xml", dest='pretty', default=4,type=int, help="Count of spaces with each plunge")
    parser.add_argument("--details",const='', nargs='?',dest='details',action='store', help="Detail informations about class")
    parser.add_argument("--search", help="Search specify class")
    parser.add_argument("--conflicts", help="Detect conflicts")
    args = parser.parse_args()
    #### servise of file #####

    input_string = read_input_file(args.input)
    output_file = open_file_to_write(args.output)

    return input_string, output_file, args.pretty, args.details, args.search

def prepare_inpudSTR_to_process(input_str):
    input_str = re.sub('\s+',' ', input_str)
    input_str = re.sub('[\n]+|[\r]+|[\t]+', '', input_str)
    input_str = re.sub('(?<=\()void(?=\))', '', input_str)
    arr_classes = re.split("}[ ]*;",input_str)              # cut text to array of classes
    return arr_classes

input_string, output_file, pretty, details, search = parse_args()
arr_classes = prepare_inpudSTR_to_process(input_string)
create_classes_and_rel(arr_classes)
parse_body_classes()
adding_inheritance()
if details or details == '':
    xml_code = generate_XML(details,output_file)
else :
    xml_code = relationship_XML(output_file)
if search:
    xml_code = parseXML_XPATH(xml_code,search)
xml_code.writexml(output_file," ","    ", "\n",encoding="UTF-8" )
