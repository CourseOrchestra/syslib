//var arrGrids = {};


function createPageDGrid(elementId, parentId, metadata) {
	require([
	         "dijit/form/Button",
	         "dijit/form/DropDownButton",
	         "dijit/form/ComboButton",
	         "dijit/form/ToggleButton",
	         "dijit/form/CurrencyTextBox",
	         "dijit/form/DateTextBox",
	         "dijit/form/NumberSpinner",
	         "dijit/form/NumberTextBox",
	         "dijit/form/TextBox",
	         "dijit/form/TimeTextBox",
	         "dijit/form/ValidationTextBox",
	         "dijit/form/SimpleTextarea",
	         "dijit/form/Textarea",
	         "dijit/form/Select",
	         "dijit/form/ComboBox",
	         "dijit/form/MultiSelect",
	         "dijit/form/FilteringSelect",
	         "dijit/form/HorizontalSlider",
	         "dijit/form/VerticalSlider",
	         "dijit/form/CheckBox",
	         "dijit/form/RadioButton",
	         "dijit/form/DataList",	     
	         
	         "dojo/store/Observable", 
	         "dojo/has",
	         "dgrid/editor", 
	         "dgrid/extensions/CompoundColumns", 
	         "dgrid/ColumnSet", 
	         "dojo/store/util/QueryResults", 
	         "dojo/on", 
	         "dgrid/Grid", 
	         "dgrid/extensions/Pagination", 
	         "ColumnResizer",
	         "dgrid/Selection", 
	         "dgrid/CellSelection", 
	         "dgrid/Keyboard", 
	         "dojo/_base/declare", 
	         "JsonRest", 
	         "dojo/store/Cache", 
	         "dojo/store/Memory", 
	         "dojo/aspect", 
	         "dojo/domReady!"
	         ],	function(
	        	 Button,DropDownButton,ComboButton,ToggleButton,CurrencyTextBox,DateTextBox,NumberSpinner,NumberTextBox,TextBox,TimeTextBox,ValidationTextBox,SimpleTextarea,Textarea,Select,ComboBox,MultiSelect,FilteringSelect,HorizontalSlider,VerticalSlider,CheckBox,RadioButton,DataList,			
			     Observable, has, editor, CompoundColumns, ColumnSet, QueryResults, on, Grid, Pagination, ColumnResizer, Selection, CellSelection, Keyboard, declare, JsonRest, Cache, Memory, aspect
			 ){
		
		var firstLoading = true;
		
		
		var mem = Memory();		
		
		var store = Observable(Cache(JsonRest({
			target:"secured/JSGridService",
			
			idProperty: "id",
			
			
			put: function(object, options){
				
				if((object.id).indexOf("addRecord") > -1 ){ // Добавление записи 
					
					object["editor"] = "addRecord";
					
					var strObject = JSON.stringify(object);
		 	    	var httpParams = gwtEditorGetHttpParams(elementId, strObject, object["editor"]);
		 	    	httpParams = eval('('+httpParams+')');

				    object[httpParams["gridContextName"]] = httpParams["gridContextValue"];	
				    object[httpParams["elementInfoName"]] = httpParams["elementInfoValue"];
				    
					var result = this.inherited(arguments);
					result.then(function(value){
							if(value.success == '1'){
//								arrGrids[parentId].refresh();				
								refreshPageDGrid(parentId);
							}
							else{
							}
							gwtShowMessage(elementId, value.message, object["editor"]);
					    }, function(err){
					    	alert("Произошла ошибка при добавлении записи:\n"+err+"\nПодробности находятся в консоли броузера.");
					    });
//				    return result;
					
				}else{  //Сохранение
					
					object["editor"] = "save";
					
					var strObject = JSON.stringify(object, function(key, value) {
						  if (
								  (key == "dirty")							  
							   || (key == "gridContextName") 
						       || (key == "elementInfoName")
						       || (key == object["gridContextName"])
						       || (key == object["elementInfoName"])
						     )
						  {
							  return undefined;						  
						  }
						  return value;
					});
		 	    	var httpParams = gwtEditorGetHttpParams(elementId, strObject, object["editor"]);
		 	    	httpParams = eval('('+httpParams+')');

		 	    	object["gridContextName"] = httpParams["gridContextName"];
		 	    	object["elementInfoName"] = httpParams["elementInfoName"];
				    object[httpParams["gridContextName"]] = httpParams["gridContextValue"];	
				    object[httpParams["elementInfoName"]] = httpParams["elementInfoValue"];
	 
				    object.dirty = JSON.stringify(grid.dirty);
				    
					var result = this.inherited(arguments);
					result.then(function(value){
							if(value.success == '1'){
							}
							else{
						        grid.dirty = JSON.parse(object.dirty);
							}
							if(value.refreshAfterSave == 'true'){
//						        grid.refresh();		
								refreshPageDGrid(parentId);
							}
							gwtShowMessage(elementId, value.message, object["editor"]);
					    }, function(err){
					        grid.dirty = JSON.parse(object.dirty);				    	
					    	alert("Произошла ошибка при сохранении данных:\n"+err+"\nПодробности находятся в консоли броузера.");
					    });
//				    return result;
					
				}
			},
			
			
			query: function(query, options){
				
				var results = null;
				
				if(firstLoading){
                    results = QueryResults(metadata["data"]["rows"]);
                    results.total = parseInt(metadata["data"]["total"]);
                    
					gwtAfterLoadData(elementId, "");
				}else{
					var sortColId  = null;
					var sortColDir = null;
					if(options && options.sort){
						for(var i = 0; i<options.sort.length; i++){
							var sort = options.sort[i];
							sortColId = grid.columns[sort.attribute].label;
							if(sort.descending){
								sortColDir = "DESC";
							}
							else{
								sortColDir = "ASC";
							}
							break;
						}
					}
					
		 	    	var httpParams = gwtGetHttpParams(elementId, options.start, options.count, sortColId, sortColDir);
		 	    	httpParams = eval('('+httpParams+')');	 	 
		 	    	
				    var params = {};
				    params[httpParams["gridContextName"]] = httpParams["gridContextValue"];	
				    params[httpParams["elementInfoName"]] = httpParams["elementInfoValue"];			    

					results = JsonRest.prototype.query.call(this, query, options, params);
					results.then(function(results){
						if(results[0]){
							gwtAfterLoadData(elementId, results[0]["liveGridExtradata"]);						
						}
					});				
				}
				
				return results;
			}
		}), mem));
		
		store.mem = mem;

		var columns = [];
		for(var k in metadata["columns"]) {
			var column = null;
			if(metadata["common"]["readonly"] || metadata["columns"][k]["readonly"]){
				column = {};
			}else{
				column =  eval("editor("+metadata["columns"][k]["editor"]+")");
				column["editable"] = true;
			}

			column["id"]        = metadata["columns"][k]["id"];
			column["parentId"]  = metadata["columns"][k]["parentId"];			
			column["field"]     = metadata["columns"][k]["id"];			
			column["label"]     = metadata["columns"][k]["caption"];
			column["sortable"]  = "true";
			column["valueType"] = metadata["columns"][k]["valueType"];
			
			if(column["editable"]){
				column["formatter"] = function columnFormatter(item){
					return item;
				};
			}else{
				column["renderCell"] = function actionRenderCell(object, value, node, options) {
					var div = document.createElement("div");
					
					if(this["valueType"] == "DOWNLOAD"){
						if(value && (value.trim()!="")){
//							div.innerHTML = "<tbody><tr><td style=\"font-size: 1em;\">"+value+"</td><td  align=\"center\" style=\"vertical-align: middle;\"><button onclick=\"gwtProcessFileDownload('"+elementId+"', '"+object.id+"', '"+this.id+"')\"><img src="+metadata["columns"][k]["urlImageFileDownload"]+" title=\"Загрузить файл с сервера\"  style=\"vertical-align: middle; align: right; width: 16px; height: 16px;  \"   ></button></p></td></tr></tbody>";
							
							div.innerHTML = 
								"<tbody>" +
									"<tr>" +
										"<td>"+value+"" +
										"</td>" +
										"<td  align=\"center\" style=\"vertical-align: middle;\">" +
										
												"<button onclick=\"gwtProcessFileDownload('"+elementId+"', '"+object.id+"', '"+this.id+"')\">" +
														"<img src="+metadata["columns"][k]["urlImageFileDownload"]+" title=\"Загрузить файл с сервера\"  style=\"vertical-align: middle; align: right; width: 8px; height: 8px;  \"   >" +
												"</button>" +

										"</td>" +
									"</tr>" +
								"</tbody>";						
							
						}else{
							div.innerHTML = value;
						}
					}else{
						div.innerHTML = value;
					}
					
					div.title = value;
					
					return div;
		        };
			}
			
			if(column["editable"]){
				column["canEdit"] = function columnCanEdit(object, value){
					result = true;
					if(object.readonly && (object.readonly.toLowerCase() == "true") ){
						result = false;
					}
					return result;					
				};
			}
			
	        
	        column["renderHeaderCell"] = function actionRenderCell(node) {
				var div = document.createElement("div");
		        if(metadata["common"]["haColumnHeader"]){
					div.style["text-align"] = metadata["common"]["haColumnHeader"];
		        }
				div.innerHTML = this.label;		        
		    	div.title = this.label;
				return div;
	        };
			
			columns.push(column);
		}
		
		
		var virtualColumnType = 0;
		var columnSets = null;
		var columnSetWidths = null;
		var compoundColumns = null;
		var allVirtualColumns = null;
		if(metadata["virtualColumns"]){
			for(var vc in metadata["virtualColumns"]) {
				if(metadata["virtualColumns"][vc]["virtualColumnType"] == "COLUMN_HEADER"){
					virtualColumnType = 1;
					break;	 				
				}
				if(metadata["virtualColumns"][vc]["virtualColumnType"] == "COLUMN_SET"){
					virtualColumnType = 2;
					break;					
				}
			}		
						
			if(virtualColumnType == 1){
				compoundColumns = [];
				allVirtualColumns = [];
				
				var i = 1;
				for(var k2 in metadata["virtualColumns"]) {
					var virtualColumn = {};
					if(metadata["virtualColumns"][k2]["virtualColumnType"] == "COLUMN_HEADER"){
						virtualColumn["id"] = "vcol"+i;
						virtualColumn["parentId"] = metadata["virtualColumns"][k2]["parentId"];
						virtualColumn["label"] = metadata["virtualColumns"][k2]["id"];					
						virtualColumn["style"] = metadata["virtualColumns"][k2]["style"];
						virtualColumn["children"] = [];
						
		
						for(var k3 in allVirtualColumns) {
							if(virtualColumn["parentId"] == allVirtualColumns[k3]["label"]){
								allVirtualColumns[k3]["children"].push(virtualColumn);
								break;
							}
						}
						
						allVirtualColumns.push(virtualColumn);
						if(!virtualColumn["parentId"]){
							compoundColumns.push(virtualColumn);
						}
		
						i++;
					} else {
						for(var k11 in columns) {
							if(columns[k11]["label"] == metadata["virtualColumns"][k2]["id"]){
								compoundColumns.push(columns[k11]);
								break;
							}
						}						
					}
				}
				
				for(var k4 in columns) {
					for(var k5 in allVirtualColumns) {
						if(columns[k4]["parentId"] == allVirtualColumns[k5]["label"]){
							allVirtualColumns[k5]["children"].push(columns[k4]);
							break;
						}
					}	
				}
			}
			
			if(virtualColumnType == 2){
				columnSets = [];
				columnSetWidths = [];
				for(var vc in metadata["virtualColumns"]) {
					var columnSet = [];
					for(var kk in columns) {
						if(columns[kk]["parentId"] == metadata["virtualColumns"][vc]["id"]){
							columnSet.push(columns[kk]);
						}
					}
					columnSetWidths.push(metadata["virtualColumns"][vc]["width"]);
					columnSets.push([columnSet]);					
				}
			}
		}
		
		
		var declareGrid = [Grid, Pagination, ColumnResizer, Keyboard];
		
		var selectionMode;
		if(metadata["common"]["selectionModel"] == "RECORDS"){
			selectionMode = "extended";			
			declareGrid.push(Selection);
		}else{
			selectionMode = "single";			
			declareGrid.push(CellSelection);
		}
		
		if(virtualColumnType == 1){
			declareGrid.push(CompoundColumns);			
		}
		
		if(virtualColumnType == 2){
			declareGrid.push(ColumnSet);			
		}
		
		var isVisiblePager = false;
		if(metadata["common"]["isVisiblePager"]){
			isVisiblePager = true;	
		}		
		var isVisibleColumnsHeader = false;
		if(metadata["common"]["isVisibleColumnsHeader"]){
			isVisibleColumnsHeader = true;	
		}
		
	    var	grid = new declare(declareGrid)({
//				store: store,
				getBeforePut: false,
				
				showFooter: isVisiblePager,
				pagingLinks: 2,
				pagingTextBox: true,
	            firstLastArrows: true,
				pageSizeOptions: [25, 50, 75, 100],
				rowsPerPage: parseInt(metadata["common"]["limit"]),

				showHeader: isVisibleColumnsHeader,
				selectionMode: selectionMode,
				loadingMessage: metadata["common"]["loadingMessage"],
//				noDataMessage: "Таблица пуста",
				pagingDelay: 50,
				deselectOnRefresh: false,				
				keepScrollPosition: true,
				readonly: metadata["common"]["readonly"]
		}, parentId);
	    arrGrids[parentId] = grid;
	    
	    
	    aspect.after( grid, 'renderRow', function( row, args ){
			if(args[0].rowstyle && (args[0].rowstyle != "")){
		    	row.className = args[0].rowstyle;				
			}
	    	return row;
	    });
	    
	    
		for(var k in metadata["columns"]) {
			grid.styleColumn(metadata["columns"][k]["id"], metadata["columns"][k]["style"]);
		}
		
		if(virtualColumnType == 0){
		    grid.set("columns", columns);
		}
		if(virtualColumnType == 1){
		    grid.set("columns", compoundColumns);
		    
		    for(var k1 in allVirtualColumns) {
				if(allVirtualColumns[k1]["style"]){
					grid.styleColumn(allVirtualColumns[k1]["id"], allVirtualColumns[k1]["style"]);
				}	
			}
		}
		if(virtualColumnType == 2){
		    grid.set("columnSets", columnSets);

			for(var vcc in columnSets) {
				if(columnSetWidths[vcc]){
					grid.styleColumnSet(vcc, "width:"+columnSetWidths[vcc]+";");					
				}
			}
		}
		
		
		for(var k in metadata["columns"]) {
			if(metadata["columns"][k]["sorting"]){
				var descending = false;
				if(metadata["columns"][k]["sorting"].toUpperCase()=="DESC"){
					descending = true;	
				}
			    grid.set("sort", [{attribute: metadata["columns"][k]["id"], descending: descending}]);
			    break;
			}
		}		
	    
	    
		grid.on("dgrid-select", function(event){
			
				if(firstLoading){
					gwtAfterClick(elementId, metadata["common"]["selRecId"], metadata["common"]["selColId"], getSelection());				
				} else {
					setTimeout(function(){
						if(!grid.readonly){
							if(grid.currentRowId != grid.row(event.grid._focusedNode).id){
								grid.currentRowId = grid.row(event.grid._focusedNode).id;
								grid.save();
							}
						}
						
						gwtAfterClick(elementId, grid.row(event.grid._focusedNode).id, grid.column(event.grid._focusedNode).label, getSelection());
					}, 50);
				}
				
		});
		grid.on(".dgrid-row:dblclick", function(event){
			gwtAfterDoubleClick(elementId, grid.row(event).id, grid.column(event).label, getSelection());
		});
		function getSelection()
		{
		    var selection = "";
		    var i = 0;
	        for(var id in grid.selection){
	            if(grid.selection[id]){
	            	if(i > 0){
		            	selection = selection+metadata["common"]["stringSelectedRecordIdsSeparator"];	
	            	}
	            	selection = selection+id;
	            	i++;
	            }
	        }
	        return selection; 
		}
		grid.on("dgrid-refresh-complete", function(event) {
			if(firstLoading){
				if(metadata["common"]["pageNumber"]){
					event.grid.gotoPage(parseInt(metadata["common"]["pageNumber"]));						
				}
				if(metadata["common"]["selectionModel"] == "RECORDS"){
					if(metadata["common"]["selRecId"]){
						event.grid.select(event.grid.row(metadata["common"]["selRecId"]));
					}
				}else{
					if(metadata["common"]["selRecId"] && metadata["common"]["selColId"]){
						for(var col in event.grid.columns){
							if(event.grid.columns[col].label == metadata["common"]["selColId"]){
								event.grid.select(event.grid.cell(metadata["common"]["selRecId"], col));
								break;
							}
						}
					}
				}
				firstLoading = false;
			}
		});
		
		grid.on("dgrid-datachange", function(event){
			if(event.value.indexOf("<") > -1){
				event.returnValue = false;
				console.log("Заблокирована строка, содержащая символ '<'");
			}
		});
		
		for(var k in metadata["columns"]) {
			grid.styleColumn(metadata["columns"][k]["id"], metadata["columns"][k]["style"]);
		}
		
	    grid.set("store", store);
		
	});
}

function refreshPageDGrid(parentId){
	
	var currentPage = arrGrids[parentId]._currentPage;  
	
	arrGrids[parentId].refresh();
	
	if(currentPage > 1){
		arrGrids[parentId].gotoPage(currentPage);		
	}
	
}

function addRecordPageDGrid(parentId){
	arrGrids[parentId].store.add({id: "addRecord_"+GenerateGUID()});
}

function savePageDGrid(parentId){
	arrGrids[parentId].save();
}

function revertPageDGrid(parentId){
//	arrGrids[parentId].revert();
	refreshPageDGrid(parentId);
}

function clipboardPageDGrid(parentId){
	var str = "";
	
	var grid = arrGrids[parentId];
	
	for(var col in grid.columns){
		str = str + grid.columns[col].label + "\t";
	}
	
	str = str + "\n";
		
    for(var id in grid.selection){
        if(grid.selection[id]){
        	for(var col in grid.columns){
        		str = str + grid.row(id).data[col] + "\t";
        	}
        	str = str + "\n";
        }
    }
	
	return str;
}

function partialUpdatePageDGrid(parentId, partialdata){
	for(var k in partialdata["rows"]) {
		if(arrGrids[parentId].row(partialdata["rows"][k].id).data){
				arrGrids[parentId].store.notify(partialdata["rows"][k], partialdata["rows"][k].id);
		}
	}
}






