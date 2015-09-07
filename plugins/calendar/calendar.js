function createCalendar(parentId, data, template) {
	require(["dijit/registry", "dojox/calendar/Calendar", "dojo/store/Memory"],
			  function(registry, Calendar, Memory){
			    	
			    	var w = registry.byId(parentId);
			    	if(w){
			    		w.destroy();			    		
			    	}
			    	
			    	var calendar = new Calendar({
			    		  date: data.metadata.date,
			    		  columnViewProps:{minHours:data.metadata.minHours, maxHours:data.metadata.maxHours},
			    		  store: new Memory({data: data.data}),
			    		  dateInterval: data.metadata.dateInterval,
						  dateIntervalSteps: data.metadata.dateIntervalSteps,
			    		  style: data.metadata.style,
			    		  editable: data.metadata.editable
			    		}, parentId);
			    	
			    	calendar.on("itemClick", function(e){
//			    		  console.log("Item clicked", e.item);
			    		gwtPluginFunc(parentId, e.item.id);
			    	});
			    	
			    	calendar.on("gridDoubleClick", function(e){
//			    		  console.log("Item clicked", e.item);
			    		gwtPluginFunc(parentId, "addItem");
			    	});
					
			    	calendar.on("onItemEditBegin", function(e){
//			    		  console.log("Item clicked", e.item);
			    		gwtPluginFunc(parentId, e.item.id + "Delete");
			    	});	
					
			    	if(!data.metadata.toolbarVisible){
				        var div = document.getElementById(parentId).parentNode;
				        if(div){
					        var div2 = div.firstChild;
					        if(div2){
					        	for (var index = 0; index < div2.childNodes.length; index++) {
					        		if(div2.childNodes[index].className == "buttonContainer"){
					        			div2.removeChild(div2.childNodes[index]);
					        		}
					        	}
					        }
				        }
			    	}
			    	
			    	
			    	
			      
			  }
	);
}
