# FilterCode
This plugin allows you filter code base on results of "find in Files" repeatedly.    
This project lives at https://github.com/happyqingye/FilterCode

## The current keyboard shortcut is:  
    `ALT+m`, `ALT+SHIFT+m`  
    
## Function introduction
This plugin is used to filter content from result of search by keywords or regular expression. The action of filter can be repeatedly and the matched items will copy into new tab for next filter. Usually used for code auditing.  

There are two filter modes in this plugin. One is `filter code` and another is `filter text`.   
### Filter Code mode 
Before start to filter code, you need to input the filter condition. You can select characters as your filter condition in current tab directly or input keyword or regular expression in input panel of condition as your filter condition.  

If you select characters in current tab and then input the keyboard shortcuts `ALT+m`, the plugin will execute the search by your selected. The results of search are copied into new tab.  

If you input the keyboard shortcuts `ALT+m` directly and no characters are selected in current tab, a input panel of condition is showed. The search is executed after you input keyword or regular expression. And the results of search are copied into new tab.  

The line of the matched item is folded in original tab. At the same time, the matched item and the related context are copied into the new tab.  

#### Add the mousemap(Option)
In order to quickly open the original file, you can define the shortcut key like below: 
<pre><code> 
[  
	{  
		"button": "button1",  
		"count": 2,  
		"press_command":"drag_select",  
		"press_args":{"by":"words"},  
		"command": "filter_code_double_click"  
	}  
]  
</code></pre>
#### Filter Code mode example
![Filter Code](https://raw.githubusercontent.com/happyqingye/image/master/FilterCode/FilterCodeProcess.gif)

### Filter Text mode 
Before start to filter text, you need to input the filter condition. You can select characters as your filter condition in current tab directly or input keyword or regular expression in input panel of condition as your filter condition.  

If you select characters in current tab and then input the keyboard shortcuts `ALT+Shift+m`, the plugin will execute the search by your selected. The results of search are copied into new tab.  

If you input the keyboard shortcuts `ALT+Shift+m` directly and no characters are selected in current tab, a input panel of condition is showed. The search is executed after you input keyword or regular expression. And the results of search are copied into new tab.  

The lines of the matched item is folded in original tab and the lines of matched item are copied into the new tab.  

There are two different points between the two filter mode. One is different keyboard shortcut(Filter Code is `ALT+m` and Filter Text is `ALT+Shift+m`). Other is different search result(in new tab, Filter Code show matched line and related context, and Filter Text only show matched line).
#### Filter Text mode example
![Filter Text](https://raw.githubusercontent.com/happyqingye/image/master/FilterCode/FilterTextProcess.gif)


