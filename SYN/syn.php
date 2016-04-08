#!/usr/bin/php
<?php
#SYN:xchudy03


/**
 * Class to store of elements format. 
 */ 
class Mystyle {
    public $expression;
    public $style;
}
/**
 * Class to store specific element and his position and fleg is opne or close
 */ 
class Tag_and_position {
    public $position;
    public $tags;
    public $open;
}

/**
 * Function to find and parse input argument
 *
 * @param string  $argumenty 	One argument from argv array
 * @param string $wanted 	 	Argument whot i finding
 * @param bool $format_allow 	If unsucessful exit is fatal
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return If function is success file URL, id fun id unsuccess false or die
 */ 
function arguments_url($argumenty,  $wanted, $format_allow){

	foreach($argumenty as $arg) {
		$pos = strpos($arg, $wanted);
		if($pos === 0){
			$exit = explode( '=',$arg );

			if (!empty($exit[1])){
				return $exit[1];
			}
			elseif ($format_allow === true){
				fwrite(STDERR, "Argumenst bed syntax!\n"); 
				exit(1);
			}
			else{break;}
		}
	}
	return false;
}

/**
 * Function to process bool arguments
 *
 * @param string $argumenty 	One argument from argv array
 * @param string $wanted 		Argument whot i finding
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return True or false
 */ 
function arguments_bool($argumenty,  $wanted){
	foreach($argumenty as $arg) {

		if(strpos($arg, $wanted) === 0 && strlen($arg) == strlen($wanted) ){
			return true;
		}
	}
	return false;
}

/**
 * Checks if in regex in not apsolutli bull shit.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return Void or die
 */ 
function chack_validity($expression){
   	$invalid="(?<!%)!$|!\+|!\*|";
   	$invalid=$invalid."(?<!%)\(\)|(?<!%)\(\||(?<!%)\|\)|";
   	$invalid=$invalid."(?<!%)\.\)|";
    $invalid=$invalid."(?<!%)\|\||(?<!%)!\||(?<!%)!\)|(?<!%)\|$|^\||";
    $invalid=$invalid."^\+|^\*|^\)";
    if(preg_match('/'.$invalid.'/', $expression)){
       	fwrite(STDERR, "Syntax error in expression!\n"); 
		exit(4);
    }
}

/**
 * Chack duplicity negations and remove them.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function chack_duplicity_neg($expression){
 if(preg_match_all('/!{2,}/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            if(strlen($match) % 2 == 0){
                $expression = str_replace($match, "", $expression);
            }else{
                $expression = str_replace($match, "!", $expression);
            }
        }
    }
    return $expression;
}

/**
 * First replace
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function first_replace($expression){
	$expression = strtr($expression, array(	
     										"[" => "\[",
     										"]" => "\]",  
     										"{" => "\{",
                                  			"}" => "\}",  
                                  			"^" => "\^", 
                                  			"$" => "\\$",
                                  			"?" => "\?",  
                                  			"\\n" => "\\\\n",
                                  			"\\t" =>"\\\\t",
                                  			"\d" => "\\\\d",
                                  			"\s" => "\\\\s", 
                                  			"\\" => "\\\\",
                                  			"/" => "\/"));  
	return $expression;
}

/**
 * Process complicated neg. Chack count od bracket end replace it
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function bracket_neg($expression){
	if(preg_match_all('/(?<!%)!\(/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            $pos = strpos($expression, $match);
            $counter = 1; 
            $pos = $pos + 2; 
            $cut_arr = str_split($expression);
            $cut_arr = array_slice($cut_arr, $pos);
            foreach ($cut_arr as $i => $char ) {
                if($char == '('){ 
                	$counter++; 
                }
                if($char == ')'){ 
                	$counter--; 
                }
                if($counter == 0){
                    break;
                }
            }
            if($counter != 0){ 
            	fwrite(STDERR, "Syntax error in expression!\n"); 
				exit(4); }
			$subs_s = substr($expression, $pos-1, ($i + $pos) - ($pos-2));
            $match = "[^".$subs_s."]";
            $expression = substr_replace($expression, $match, $pos-2, ($i + $pos) - ($pos-2) +1);
        }
    }
    return $expression;
}

/**
 * Process easy neg.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function negation($expression){
	if(preg_match_all('/(?<!%)(!%.|!.)/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            $pos = strpos($expression, $match);
            $length = strlen($match);
            $replace = str_replace("!", "", $match);
            $match = str_replace($match, "[^". $replace."]",$match);
            $expression = substr_replace($expression, $match, $pos, $length);         
        }
    }
    return $expression;    
}

/**
 * Translate dots.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function dots_process($expression){
	if(preg_match_all('/[^\(|\%|\.]\.[^\*|\+|\.]/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            $pos = strpos($expression, $match);
            $length = strlen($match);
            $match = str_replace($match, str_replace(".", "", $match),$match);
            $expression = substr_replace($expression, $match, $pos, $length);         
        }
    }
    if(preg_match('/(?<!%)\./', $expression)){ 
    	fwrite(STDERR, "Syntax error in expression!\n"); 
		exit(4);
	}
	return $expression;
}

/**
 * Main trasnlate function. Change special chars to regular chars.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function translate_special_char($expression){
	$matches = array();
    if(preg_match_all('/(?<!%)%(s|d|a|l|L|w|W|n|t)/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            $pos = strpos($expression, $match);
            $length = strlen($match);
            $match = strtr($match, array("%s" => "\s",
                                        "%d" => "\d",
                                        "%a" => "(.|\s)",
                                        "%l" => "[a-z]",
                                        "%L" => "[A-Z]",
                                        "%w" => "[a-zA-Z]",
                                        "%W" => "[a-zA-Z0-9]",
                                        "%n" => "\n",
                                        "%t" => "\t"));
            $expression = substr_replace($expression, $match, $pos, $length);
        }
    }       
   if(preg_match_all('/(?<![^%]%)%(\.|!|\||\*|\+|\(|\))/', $expression, $matches)){
        foreach ($matches[0] as $match) {
            $pos = strpos($expression, $match);
            $length = strlen($match);
            $match = strtr($match,array("%!" => "!",
                                        "%|" => "\|",
                                        "%*" => "\*", 
                                        "%+" => "\+",
                                        "%(" => "\(", 
                                       	"%)" => "\)",
            							"%." => "\."
            							));
            $expression = substr_replace($expression, $match, $pos, $length);
        }
    }        
    return $expression;      
}

/**
 * Check end remove duplicity of percents.
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified expression
 */ 
function remove_duplicity_percent($expression){
	if(preg_match_all('/%+/', $expression, $matches,PREG_OFFSET_CAPTURE)){
        $shift = 0;
        foreach ($matches[0] as $match) {
        	$length = strlen($match[0]);
            if($length % 2 == 0){
            	$whot = str_repeat("%", ($length / 2));
            	$expression = substr_replace($expression,$whot ,$match[1]- $shift, $length);
            	$shift = $length / 2;
            }else{
                fwrite(STDERR, "Syntax error in expression!\n"); 
				exit(4);
            }
        }
    }
    return $expression;
}
/**
 * Translate regex from pseudo language to regular PHP regex if its posible
 *
 * @param string $expression 	Regec to translate
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return Translate regex or program die
 */ 
function convert_expression($expression){
	
	$expression = preg_replace('/\*{2,}/', '*', $expression);
    $expression = preg_replace('/\+{2,}/', '+', $expression);
    $expression = preg_replace('/(\+|\*)?(\+\*|\*\+)+(\+|\*)?/', '*', $expression);

	chack_validity($expression);
	$expression = chack_duplicity_neg($expression);
    $expression = first_replace($expression);
    $expression = bracket_neg($expression);
    $expression = negation($expression);
    $expression = dots_process($expression);
    $expression = translate_special_char($expression);
    $expression = remove_duplicity_percent($expression);
    return $expression;
}

/**
 * Chack and parse formating file
 *
 * @param file $format 	Pointer to open file
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return Array of Mystyle objects. 
 */ 
function process_format($format){
	if ($format !== false ){
		$stack_style = array();
		$tmp_stylp;
		while(!feof($format)){
	    	$tmp_style = explode( "\t",fgets($format),2);
	    	if (empty($tmp_style[0]) && empty($tmp_style[1])){continue;}
	    	if (strlen($tmp_style[0]) != 0 ){
		    	$obj = new Mystyle();
		    	$first = true;
		    	$obj->expression = "/".convert_expression($tmp_style[0])."/";
		    	$obj->style = $tmp_style[1];
		    	array_push($stack_style, $obj);
	    	}
	    	else{
                fwrite(STDERR, "Empty regex!\n"); 
				exit(4);
	    	}

	  	}
	}
	else{
		return false;
	}
	return $stack_style;
}

/**
 * Function on convert tags form formating file to html tags
 *
 * @param string $style 	Line of stailing elements
 * @param bool $opening 	True if its i need opening tags, false if i need closing tags
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return String of html elements 
 */ 
function decode_tags($style, $opening){
	$style = str_replace(' ', '', $style);	#remow spaces
	$style = str_replace("\n", '', $style);	#remow simbols of end of line
	$style = str_replace("\t", '', $style);	#remow simbols of end of line
	$arr_tag = explode( ',',$style);			#divide string as semicolon
	$ret_tag_str = "";
	foreach ($arr_tag  as $tag){
		$ok = true;		
		switch ($tag) {
    		case "bold":
    			$ret_tag_str = ($opening === true)? $ret_tag_str."<b>":"</b>".$ret_tag_str; continue;
    		case "italic":
    			$ret_tag_str = ($opening === true)? $ret_tag_str."<i>":"</i>".$ret_tag_str; continue;
    		case "underline":
    			$ret_tag_str = ($opening === true)? $ret_tag_str."<u>":"</u>".$ret_tag_str; continue;
    		case "teletype":
    			$ret_tag_str = ($opening === true)? $ret_tag_str."<tt>":"</tt>".$ret_tag_str; continue;
			default:
				$ok = false;
				break;
		}
		if (strpos($tag, "color:") === 0){
			$tmp_list = explode( ':',$tag);
			preg_match("/[^A-F0-9]/",$tmp_list[1] ,$match);
			if(!empty ($match)){
				fwrite(STDERR, "Syntax error in color of text!\n"); 
				exit(4); }
			if(hexdec($tmp_list[1]) < hexdec(0) || hexdec($tmp_list[1]) > hexdec("FFFFFF")){$OK = false; break;}
			$ret_tag_str = ($opening === true)? $ret_tag_str."<font color=#".(string)$tmp_list[1].">" : "</font>".$ret_tag_str;
    		$ok = true;
    		continue;
		}
		else if (strpos($tag, "size:") === 0){
			$tmp_list = explode( ':',$tag);
			
			preg_match("/[^1-8]/",  $tmp_list[1], $match);
			
			if(!empty ($match)){
				fwrite(STDERR, "Syntax error in size of text!\n"); 
				exit(4); }
			if($tmp_list[1] < 1 || $tmp_list[1] > 8){$OK = false; break;}
			$ret_tag_str = ($opening === true)? $ret_tag_str."<font size=".(string)$tmp_list[1].">" : "</font>".$ret_tag_str;
    		$ok = true;
    		continue;
		}
		if ($ok === false){ break; }
	}
	if ($ok === false){
		fwrite(STDERR, "Syntax error in formating file!\n"); 
		exit(4);
	}
	return $ret_tag_str;
}

/**
 * BubbleSort for sorting array (static)
 *
 * @param array $arr 	Array to sort
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return Sorted array 
 */ 
function bubbleSort(array $arr){
    $n = sizeof($arr);
    for ($i = 1; $i < $n; $i++) {
        for ($j = $n - 1; $j >= $i; $j--) {
            if($arr[$j-1]->position > $arr[$j]->position) {
                $tmp = $arr[$j - 1];
                $arr[$j - 1] = $arr[$j];
                $arr[$j] = $tmp;
            }
        }
    }
    return $arr;
}

/**
 * Function to reverse order of closing elements on specific position
 *
 * @param array $arr_tags_position 	Array of objects "Tag_and_position" (class defined up) 
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return New modified array
 */
function reverse_ending_tags($arr_tags_position){
	$new_array = array();
	$open_tag = array();
	$close_tag = array();
	$point = false;
	if(!empty($arr_tags_position)){
		$last_pos = $arr_tags_position[0]->position;	#load first element
	}

	foreach ($arr_tags_position as $value) {
		if($value->open){
			if($last_pos == $value->position){
				array_push($open_tag, $value);
			}
			else {
				$new_array = array_merge ($new_array, array_reverse($close_tag), $open_tag);
				unset($open_tag); $open_tag = array();
				unset($close_tag); $close_tag = array();
				$last_pos =$value->position;
				array_push($open_tag, $value); 		
			}
		}
		else{
			if($last_pos == $value->position){
				array_push($close_tag, $value);
			}
			else {
				$new_array =  array_merge ($new_array, array_reverse($close_tag), $open_tag );
				unset($open_tag); $open_tag = array();
				unset($close_tag);$close_tag = array();
				$last_pos =$value->position;
				array_push($close_tag, $value); 			
			}	
		}
	}
	$new_array =  array_merge ($new_array, array_reverse($close_tag), $open_tag );
	return $new_array;
}

/**
 * Main function of program. Function add html element to program on defined places
 *
 * @param array $arr_stylesheets 	Array of objects "Mystyle" (class defined up, parse format)
 * @param bool 	$arg_br 			Flag if was use --br
 * @param file 	$input 				Pointer to open file to read
 * @param file 	$output 			Pointer to open file to write
 * 
 * @author Andrej Chudy <xchudy03@stud.fit.vutbr.cz>
 * @return Nothing its void function
 */
function add_formating_tags($arr_stylesheets, $arg_br, $input, $output){
	$arr_tags_position = array();		#array of string tags and positions
	$input_txt =  stream_get_contents($input);		#read input file
	$output_txt = "";
	$output_txt = $input_txt;
	if($arr_stylesheets !== false){		#if formating file was defined
		foreach($arr_stylesheets as $stylesheet){		#iterating over each element of stilesheet
			$ret_code = @preg_match_all($stylesheet->expression, $input_txt, $arr_matches, PREG_OFFSET_CAPTURE);#apply regular expressions
			if($ret_code === false){
				fwrite(STDERR, "Unvalid syntax of expression!\n"); 
				exit(4);
			}

			$open_tag = decode_tags($stylesheet->style, true);	#create formating string open tags
			$close_tag = decode_tags($stylesheet->style, false);	#create formating string close tags

			foreach ($arr_matches[0] as $match){
				if (strlen($match[0]) != 0){
					$obj = new Tag_and_position();	#reate object whit string tag end position where it must be use for opnening
					$obj->position = $match[1];
					$obj->tags = $open_tag;
					$obj->open = true;
					array_push($arr_tags_position, $obj);	#add to array
					$obj2 = new Tag_and_position(); #reate object whit string tag end position where it must be use for closing
					$obj2->position = $match[1] + strlen($match[0]);
					$obj2->tags = $close_tag; 
					$obj2->open = false;
					array_push($arr_tags_position, $obj2);	#add to array
				}
			}
		}
		
		$arr_tags_position = bubbleSort($arr_tags_position);
		$arr_tags_position = reverse_ending_tags($arr_tags_position);
		$arr_tags_position = array_reverse($arr_tags_position);

	}
	
	
	if($arr_stylesheets !== false){
		foreach($arr_tags_position as $tags_position){
			$output_txt =  substr_replace($output_txt,$tags_position->tags ,$tags_position->position, 0);	#insert tags on positions
		} 
	}

	if ($arg_br === true){ 
			$output_txt = str_replace("\n", "<br />\n", $output_txt);
	}

	fwrite($output,$output_txt);	#write to file
}

####################### START MAIN ##################################

if (arguments_bool($argv, "--help") == true){
	if (count($argv) == 2){
		echo "\nSyntax highlighting. Projekt IPP 2016\n"
		."Autor: Andrej Oliver Chudy   LogIN: xchudy03\n\n"
		."--format=filename => Determining the file formatting\n"
		."--input=filename  => Determining the file input\n"
		."--output=filename => Determining the file output\n"
		."--br => html element <br /> at the end of each line\n";
		exit (0);
	}
	fwrite(STDERR, "Bed caunt of arguments!\nFor more information use \"syn.php --help\" .\n");
	exit (1);
}

$arg_br = arguments_bool($argv, "--br");		#find argument --br
$format = arguments_url($argv, "--format=",false);	#find argument --format
$input  = arguments_url($argv, "--input=",true);		#find argument --input
$output = arguments_url($argv, "--output=",true);	#find argument --output
$arg_counter = 0;

if ($arg_br !== false){$arg_counter++;}

if ($format !== false){
	$file_path = $format;
	$format = @fopen($format,'r');
	if ($format !== false){
		$format = ('' == file_get_contents( $file_path ))? false : $format;
	}
	$arg_counter++;
}

if ($input === false){
	$input = @fopen('php://stdin','r');
}
else{
	$input = @fopen($input,'r');
	$arg_counter++;
}
if ($output === false){$output = @fopen('php://stdout','w');}
else{
	$output = @fopen($output,'w');	
	$arg_counter++;
}
if (count ($argv) - 1 != $arg_counter ){
	fwrite(STDERR, "Bad count of arguments!\nFor mor information use \"syn.php --help\" .\n"); 
	exit(1);
}

if($input === false){fwrite(STDERR, "Not such file or directory inpud file!\n"); exit(2);}
if($output === false){fwrite(STDERR, "Not such file or directory output file!\n"); exit(3);} 

$exp_style_arr = process_format($format);
add_formating_tags($exp_style_arr, $arg_br,$input,$output);

@fclose($input);
@fclose($output);
