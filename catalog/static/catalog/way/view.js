function enter_edit_mode() {
	$('#ap-add-child-button').show();
	$('#ap-save-button').show();
	$('#ap-edit-button').hide();
}

function leave_edit_mode() {
	$('#ap-add-child-button').hide();
	$('#ap-save-button').hide();
	$('#ap-edit-button').show();
}

function save_changes() {
	leave_edit_mode();
}
function initialize_toolbar() {
	$('#ap-edit-button').click(enter_edit_mode);
	$('#ap-save-button').click(save_changes);
}