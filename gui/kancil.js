
$(document).ready(function(){  
    t = 0;
    $('#send').click(function(e){
        e.preventDefault();
        var prompt = $("#prompt").val().trimEnd();
        console.log(prompt);
        if(prompt == ""){
            $("#response").text("Please ask a question.");
        }
        else{            
            function myTimer() {
                $("#response").html("<p>Waiting for response ... " + t + "s</p>");
                t++;
            }
            const myInterval = setInterval(myTimer, 1000);          
            $.ajax({
                url: "/query",
                method:"POST",
                data: JSON.stringify({input: prompt}),
                contentType:"application/json; charset=utf-8",
                dataType:"json",
                success: function(data){
                    $("#response").html("<b>Response: </b> <p>" + data.response + "</p>");
                    if(data.sqlString){
                        $("#sqlString").html("<b>SQL Query: </b> <p>" + data.sqlString + "</p>");                        
                    } else {
                        $("#sqlString").html("");                        
                    }
                    if(data.kustoString){
                        $("#kustoString").html("<b>Kusto Query: </b> <p>" + data.kustoString + "</p>");                    
                    } else {
                        $("#kustoString").html("");                    
                    }
                    $("#checking").html("<p>" + data.checking + "</p>");                    
                    $("#kustoString").append("<small class='text-secondary'>Responded in " + t + " seconds</small>");
                    $("#source").html("<small class='text-secondary'>" + data.source + "</small>");    
                    clearInterval(myInterval);
                    t = 0;
                }
              })   
              
        }
    });     
});  

