$(document).ready(function () {
	$("form[name='profile']").each(function () {
		var defiline_profile_form = this;
		
		var MAX_CHILDREN = 10;
		
		$(defiline_profile_form).on("change", 'input[name="zip"]', function (event) {
			openerp.jsonRpc("/profile/get_location", 'call', {
	            'zip': this.value})
	        .then(function (better_zips) {
	        	$('select[name="city"]').find('option').remove().end();
	        	_.forEach(better_zips, function(better_zip) {
	        		$('select[name="city"]').append('<option value='+better_zip.city+'>'+better_zip.city+'</option>').val(better_zip.city);
	        	});
        	});
		});
		
		// Setup children
		var years = [];
		var date  = new Date();
		
		for(var i = date.getFullYear(); i >= date.getFullYear() - 100; i--)
			years.push('<option value="' + i + '">' + i + '</option>');
		
		$("#child_birthyear").html(years.join(''));
		
		function add_child_entry(child_id) {
			var by = child_id.substr(0, 4);
			var s  = child_id.substr(4, 1);
		
			$("#children_view tbody").append(
				'<tr>' +
					'<td>' + by + '</td>' +
					'<td>' + s + '</td>' +
					'<td class="delete_child_entry" child_id="' + by + s + '"><img src="http://www.opinions.be/defiline/static/src/images/delete.png" alt="delete"/></td>' +
				'</tr>'
			);
		}

		function delete_child_entry(child_id) {
			var children  = $("#children").attr('value').split(',').sort();
			var count     = (children[0] == '' ? 0 : children.length);
			
			for(var i = 0; i < count; i++) {
				if(children[i] == child_id) {
					children.splice(i, 1);
					break;
				}
			}
			
			$("#children").attr('value', children.sort().join(','));
		}
		
		function refresh_children_view() {
			var children  = $("#children").attr('value').split(',').sort();
			var count     = (children[0] == '' ? 0 : children.length);
			
			$("#children_view tbody").html('');
			for(var i = 0; i < count; i++)
				add_child_entry(children[i]);
			
			$('#children_view tr:odd').addClass('table-row-odd');
			$('#children_view tr:even').addClass('table-row-even');
			
			$(".delete_child_entry").click(function(ev) {
				delete_child_entry($(this).attr('child_id'));
				refresh_children_view();
			});
		}
		
		refresh_children_view();
		
		$("#child_add").click(function(ev) {
			var birthyear = $("#child_birthyear").val();
			var sex       = $("#child_sex").val();
			var children  = $("#children").attr('value').split(',');
			var count     = (children[0] == '' ? 0 : children.length);
			
			if(count < MAX_CHILDREN) {
				if(count == 0)
					children[0] = '' + birthyear + sex;
				else
					children.push('' + birthyear + sex);
				
				$("#children").attr('value', children.sort().join(','));
			} else {
				alert("Vous ne pouvez pas ajouter un autre enfant");
			}
			
			refresh_children_view();
			$(element).off('click').on('click', function() {
			});
		});
		
		var val = $("input[name='has_car']:checked").val();
		if(val == "True") {
			$("div[name='car_info']").show('quick');
		} else {
			$("div[name='car_info']").hide('quick');
		}
		
		$("input[name='has_car']").click(function(ev) {
			var val = $("input[name='has_car']:checked").val();
			if(val == "True") {
				$("div[name='car_info']").show('quick');
			} else {
				$("div[name='car_info']").hide('quick');
			}
		});
		
		var val = $("input[name='is_smoker']:checked").val();
		if(val == "True") {
			$("div[name='tobacco_info']").show('quick');
		} else {
			$("div[name='tobacco_info']").hide('quick');
		}
		
		$("input[name='is_smoker']").click(function(ev) {
			var val = $("input[name='is_smoker']:checked").val();
			if(val == "True") {
				$("div[name='tobacco_info']").show('quick');
			} else {
				$("div[name='tobacco_info']").hide('quick');
			}
		});

		var val = $("select[name='marital_status'] option:selected").val();
		if(val == 'cohabiting' || val == 'married') {
			$("div[name='partner_diploma_info']").show('quick');
		} else {
			$("div[name='partner_diploma_info']").hide('quick');
		}
		
		$("select[name='marital_status']").change(function(ev) {
			var val = $("select[name='marital_status'] option:selected").val();
			if(val == 'cohabiting' || val == 'married') {
				$("div[name='partner_diploma_info']").show('quick');
			} else {
				$("div[name='partner_diploma_info']").hide('quick');
			}
		});
		
		var val = $("select[name='professional_status'] option:selected").val();
		if(val == 'employee' || val == 'worker' || val == 'independant') {
			$("div[name='profession_info']").show('quick');
		} else {
			$("div[name='profession_info']").hide('quick');
		}
		
		$("select[name='professional_status']").change(function(ev) {
			var val = $("select[name='professional_status'] option:selected").val();
			if(val == 'employee' || val == 'worker' || val == 'independant') {
				$("div[name='profession_info']").show('quick');
			} else {
				$("div[name='profession_info']").hide('quick');
			}
		});
		
		var val = $("input[name='hypermarket']:checked").val();
		if(val == "Other") {
			$("input[name='hypermarket_other']").show('quick');
		} else {
			$("input[name='hypermarket_other']").hide('quick');
		}
		
		$("input[name='hypermarket']").change(function(ev) {
			var val = $("input[name='hypermarket']:checked").val();
			if(val == "Other") {
				$("input[name='hypermarket_other']").show('quick');
			} else {
				$("input[name='hypermarket_other']").val('');
				$("input[name='hypermarket_other']").hide('quick');
			}
		});

		$("[name='phone']").inputmask();
	});
	
	$("form[name='registration']").each(function () {
		var defiline_profile_form = this;
		
		var session_lang = openerp.website.get_context().lang;
		if (session_lang == "fr_BE"){
			$.get('/defiline/static/src/docs/general_conditions_fr.txt', function(data) {
				$("#general_conditions").html(data);
			});
		}else if (session_lang == "en_US"){
			$.get('/defiline/static/src/docs/general_conditions_en.txt', function(data) {
				$("#general_conditions").html(data);
			});
		}else if (session_lang == "nl_BE"){
			$.get('/defiline/static/src/docs/general_conditions_nl.txt', function(data) {
				$("#general_conditions").html(data);
			});
		}

		$("#general_conditions_show").click(function() {
			$("#general_conditions").show('slow');
			$("#general_conditions_show").hide();
			$("#general_conditions").attr("disabled", "disabled");
		});
		
		$("[name='birthdate']").inputmask();
	});
});



