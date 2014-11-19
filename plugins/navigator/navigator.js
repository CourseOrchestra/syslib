function createNavigator(parentId, data, template) {
	require(["dijit/registry", "dijit/layout/AccordionContainer", "dijit/layout/ContentPane", 
	         "dojo/aspect", "put-selector/put", "dojo/_base/lang", "dojo/store/Memory", "dgrid/Selection", "dojo/on", "dgrid/OnDemandGrid", "dgrid/Keyboard", "tree", "dojo/_base/declare", 
	         "dojo/domReady!"],
			  function(
					  registry, AccordionContainer, ContentPane,
					  aspect, put, lang, Memory, Selection, on, Grid, Keyboard, tree, declare 
					  ){
		
		
    	var w = registry.byId(parentId);
    	if(w){
    		w.destroy();			    		
    	}
    	
    	
    	function getTreeIcon(str){
    		return "<a><img border=\"0\" src=\""+str+"\"></a>";
    	}
    	
    	function fillData(arr, obj, num){
    		
    		if(obj["level"+num] && !obj["level"+num].length){
    			obj["level"+num] = [obj["level"+num]];
    		}
    		
    		for(var k in obj["level"+num]) {
    			var parent = null;
    			if(num > 1){
    				parent = obj["@id"];
    			}
    			
    			var hasChildren = 0;
    			if(obj["level"+num][k]["level"+(num+1)]){
    				hasChildren = 1;	
    			}
    				
    			arr.push({id: obj["level"+num][k]["@id"], 
    				      name: obj["level"+num][k]["@name"],
    				      parent: parent,
    				      HasChildren: hasChildren,
    				      TreeGridNodeCloseIcon: obj["level"+num][k]["@closeIcon"],
    				      TreeGridNodeOpenIcon: obj["level"+num][k]["@openIcon"],
    				      TreeGridNodeLeafIcon: obj["level"+num][k]["@leafIcon"],
    				      open: obj["level"+num][k]["@open"],
    				      selectOnLoad: obj["level"+num][k]["@selectOnLoad"],
    				      classNameRow: obj["level"+num][k]["@classNameRow"] 
    			
    				      });
    			
    			if(hasChildren == 1){
        			fillData(arr, obj["level"+num][k], num+1);    				
    			}
    		}
    	}
    	
    	
	    var aContainer = new AccordionContainer({}, parentId);
	    
		if(!data.navigator.group.length){
			data.navigator.group = [data.navigator.group];
		}	    
	    
		for(var k in data.navigator.group) {
			
			if(data.navigator.group[k]["@hide"]  && data.navigator.group[k]["@hide"].toLowerCase()=="true"){
				continue;
			}
			
			
			var groupData = [];
			fillData(groupData, data.navigator.group[k], 1);

			
	    	store = new Memory({
	    		data: groupData,
	    		
	    		getChildren: function(parent, options){
	    			// Support persisting the original query via options.originalQuery
	    			// so that child levels will filter the same way as the root level
	    			return this.query(
	    				lang.mixin({}, options && options.originalQuery || null,
	    					{ parent: parent.id }),
	    				options);
	    		},
	    		mayHaveChildren: function(parent){
	    			return parent.HasChildren == 1;
	    		},
	    		query: function (query, options){
	    			query = query || {};
	    			options = options || {};
	    			
	    			if (!query.parent && !options.deep) {
	    				// Default to a single-level query for root items (no parent)
	    				query.parent = undefined;
	    			}
	    			return this.queryEngine(query, options)(this.data);
	    		}
	    	});

	    	
	    	var classNameGrid="";
	        if(data.navigator.group[k]["@classNameGrid"] && (data.navigator.group[k]["@classNameGrid"].trim()!="")){
	        	classNameGrid=data.navigator.group[k]["@classNameGrid"];
	        }
	        classNameGrid=classNameGrid+" plugin-navigator-grid";
	        
	    	var classNameColumn="";
	        if(data.navigator.group[k]["@classNameColumn"] && (data.navigator.group[k]["@classNameColumn"].trim()!="")){
	        	classNameColumn=data.navigator.group[k]["@classNameColumn"];
	        }
	        classNameColumn=classNameColumn+" plugin-navigator-grid-column";
	        
	        var  grid = new declare([Grid, Selection, Keyboard])({
	        	
	        	className: classNameGrid,
	        	
				store: store,
				
//				showHeader: false,
				selectionMode: "single",
				
				columns: [tree({
					
					className: classNameColumn,					
					
					id: "name",
					field:"name",					
					
					shouldExpand: function columnShouldExpand(row, level, previouslyExpanded){
						if(row.data.selectOnLoad){
							this.grid.select(row);	
							if(data.navigator["@afterReloadAction"] && data.navigator["@afterReloadAction"].toLowerCase()=="true"){
					    		gwtPluginFunc(parentId, row.data.id);  
							}
						}
						return row.data.open;
					},
					
					formatter: function columnFormatter(item){
						return item;
					},
					
					renderExpando: function columnRenderExpando(level, hasChildren, expanded, object) {
					
				        var dir = this.grid.isRTL ? "right" : "left",
							cls = ".dgrid-expando-icon",
							node;
				        
						if((object.HasChildren) && (object.HasChildren == 1)){
							if(object.TreeGridNodeLeafIcon && object.TreeGridNodeLeafIcon.trim().length > 0){
								cls += ".ui-icon-triangle-1-" + (expanded ? "se" : "e");									
							}else{
								cls += ".ui-icon.ui-icon-triangle-1-" + (expanded ? "se" : "e");									
							}
						}
						node = put("div" + cls + "[style=width:20px; margin-" + dir + ": " +
							(level * (this.indentWidth || 9)) + "px; float: " + dir + "]");
						
						node.innerHTML = "&nbsp;"; // for opera to space things properly							
						if(object.HasChildren && (object.HasChildren == '1')){
							if(expanded){
								if(object.TreeGridNodeOpenIcon && object.TreeGridNodeOpenIcon.trim().length > 0){
									node.innerHTML = getTreeIcon(object.TreeGridNodeOpenIcon);
								}
							}
							else{
								if(object.TreeGridNodeCloseIcon && object.TreeGridNodeCloseIcon.trim().length > 0){
									node.innerHTML = getTreeIcon(object.TreeGridNodeCloseIcon);
								}
							}
						}else{
							if(object.TreeGridNodeLeafIcon && object.TreeGridNodeLeafIcon.trim().length > 0){
								node.innerHTML = getTreeIcon(object.TreeGridNodeLeafIcon);
							}
						}
	
	  				    node.title = object.name;							
	
						return node;
					}
				})]
			});
	        
	        aspect.after( grid, 'renderRow', function( row, args ){
				if(args[0].classNameRow && (args[0].classNameRow.trim() != "")){
			    	row.className = args[0].classNameRow;				
				}
		    	return row;
		    });
	        
	        
	        
	        grid.on("dgrid-select", function(event){
	        	
//	        	console.log(event);
/*	        	
				if(event.target.className.indexOf("expando-icon") != -1){
					return;
				}
*/				
				
	    		gwtPluginFunc(parentId, event.rows[0].id);
	        });
	        
			grid.on(".dgrid-row:click", function(event){
//	        	console.log(event);
			});
			
			
			
	        if(data.navigator.group[k]["@styleColumn"] && (data.navigator.group[k]["@styleColumn"].trim()!="")){
				grid.styleColumn("name", data.navigator.group[k]["@styleColumn"]);
	        }
	        
	        grid.set("showHeader", false);
	        
	        grid.refresh();	    

	        
	        var classNameTitle="";
	        if(data.navigator.group[k]["@classNameTitle"] && (data.navigator.group[k]["@classNameTitle"].trim()!="")){
	        	classNameTitle="class=\""+data.navigator.group[k]["@classNameTitle"]+"\"";
	        }
	        var styleTitle="";
	        if(data.navigator.group[k]["@styleTitle"] && (data.navigator.group[k]["@styleTitle"].trim()!="")){
	        	styleTitle="style=\""+data.navigator.group[k]["@styleTitle"]+"\"";
	        }
	        var iconTitle="";
	        if(data.navigator.group[k]["@icon"] && (data.navigator.group[k]["@icon"].trim()!="")){
	        	iconTitle="<img border=\"0\" src=\""+data.navigator.group[k]["@icon"]+"\">";
	        }
	        var title = "<p "+classNameTitle+" "+styleTitle+">"+iconTitle+""+data.navigator.group[k]["@name"]+"</p>";
	        
	        
		    var pane = new ContentPane({
		        title: title,
		        content: grid
		    });
		    aContainer.addChild(pane);		    
			if(data.navigator.group[k]["@open"] && data.navigator.group[k]["@open"].toLowerCase()=="true"){
				aContainer.selectedPane = pane;  
			}
		}
		
	    aContainer.startup();		
	    
		if(aContainer.selectedPane){
		    aContainer.selectChild(aContainer.selectedPane, false);			
		}
		
			      
			  }
	);
}
