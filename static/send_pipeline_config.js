function reloadPage(){
  window.location.reload();
  // sendPipelineParameters();
  // $(window).bind("load", function() {
  //   sendPipelineParameters();
  // });
}

function sendPipelineParameters() {
  var backendFb = document.getElementById("backend-fb");
  var blocks_details = document.querySelectorAll('details');
  var pipeline_parameters = [];
  var block_parameters;
  var i = 0;
  console.log("Hello fom JS.");
  while(blocks_details[i]){

    var params_block_single = [];

    // Find out the block type, to label the parameter set:
    var block_type = blocks_details[i].querySelector('summary').textContent;
    var block_enabled = blocks_details[i].querySelector('.block_enabled').checked;
    console.log("Tipo do objeto: ", typeof(block_type))
    console.log("block_enabled: ", block_enabled);

    params_block_single.push(block_type);

    // For lambda blocks:
    if(block_type == 'lambda'){
      console.log('Lambda Block Found!')

      var obj = {};

      // Assign Lambda Block Enabled:
      var lambda_en = blocks_details[i].querySelector('.block_enabled').value;
      obj['id_lambda_en'] = block_enabled;
      params_block_single.push(obj);

      // Assign Lambda Block Code (in base64 encoding):
      var code_block = blocks_details[i].querySelector('textarea').value;
      var code_block_b64 = btoa(code_block);
      obj['id_lambda_code'] = code_block_b64;
      params_block_single.push(obj);
      
      pipeline_parameters[i] = params_block_single;
    }
    else{
      // Get parameters by general id:
      block_parameters = blocks_details[i].querySelectorAll('table tr .tg-val input');
      
      // Scan the parameters dict and make the pair {param:value}
      var j = 0
      while(block_parameters[j]){
        
        var block_enabled = blocks_details[i].getElementsByClassName("block_enabled").checked
        var obj = {};
        
        if(block_parameters[j].className == "block_enabled")
          obj[block_parameters[j].id] = block_parameters[j].checked;
        else
          obj[block_parameters[j].id] = block_parameters[j].value;
        
          params_block_single.push(obj);

        // Increment for the next pair parameters over the current block
        j++;
      }
      if(params_block_single.length > 0)
        pipeline_parameters[i] = params_block_single;
      
      // Increment for the next block of parameters
    }
    i++;
  }

  //  Transmition to the back-end:
   $.ajax({
     type: "POST",
     url: "/atualiza_pipeline",
     data: JSON.stringify(pipeline_parameters),
     contentType: "application/json",
     dataType: 'json',
     success: function(result) {
      backendFb.innerHTML = result.backend_fb; 
      console.log("result.backend_fb: ", result.backend_fb)
     } 
   });
  }