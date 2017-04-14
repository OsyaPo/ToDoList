//https://habrahabr.ru/post/42426/
//https://www.w3schools.com/jquery/ajax_getjson.asp


$(document).ready(function () {
    //https://bootstrap-datepicker.readthedocs.io/en/latest/
    $('.datepicker').datepicker({
        format: 'yyyy/mm/dd',
        startDate: '+0d',
        todayHighlight: true,
        weekStart: 1
    });

    //http://bootstrap-colorselector.flaute.com/
    $('#color').colorselector();

    function reloadTasks() {
        // load daily tasks
        loadTasks(true);

        // load long-term tasks
        loadTasks(false);
    }
    
    //adds tasks to the table "My task for today"
    function loadTasks(forToday) {
        var url, container;
        if (forToday === true) {
            container = '#list_table > tbody';
            url = 'getTasks';
        }
        else if (forToday === false) {
            url = 'getLtTasks';
            container = '#lt_list_table > tbody';
        }
        else return;

        $.ajax({
            method: "GET",
            url: url
        }).success(function (data) {
            // remove table rows
            $(container).empty();

            var html = [];
            var className = "";
            for (var task in data) {
                if (data[task].status == "checked") {
                    className = "task_done";
                }
                else className = "";

                html.push('<tr><td>' + data[task].date + '</td><td>' + data[task].time + '</td><td class="col-md-8 task_text ' + className + '">' + data[task].task + '</td>\
                <td><span class="' + data[task].label_color + ' ">' + data[task].label_text + '</span></td>\
                <td><button class="btn btn-default trash" data-container="body" data-toggle="confirmation" data-placement="top" data-singleton="true" data-taskid="' + data[task].Id + '"><i class="fa fa-trash-o" aria-hidden="true"></i></button></td>\
                <td><button class="btn btn-default change " data-toggle="modal" data-target="#myModal" data-taskid="' + data[task].Id + '"><i class="fa fa-pencil" aria-hidden="true"></i></button></td>\
                <td><button class="btn btn-default check "  data-taskid="' + data[task].Id + '"><i class="fa fa-check-square-o" aria-hidden="true"></i></button></td></tr>');
            }
            //http://stackoverflow.com/questions/171027/add-table-row-in-jquery
            $(container).append(html.join(''));

            $('[data-toggle="confirmation"]').confirmation({ container: "body", btnOkClass: "btn btn-sm btn-danger", btnCancelClass: "btn btn-sm btn-primary", onConfirm: function (event, element) { element.trigger('confirm'); } });
               
        });
    }
   
    
    // change status of the task
    $('.table-responsive>table').on("click", ".check", function () {
        var button = this;
        $.ajax({
            method: "POST",
            url: '/changeStatus',
            data: { task_id: $(button).data("taskid") }
        }).success(function () {
            reloadTasks();
        });
    });

    //http://stackoverflow.com/questions/34634047/bootstrap-confirmation-onconfirm-not-firing
    // delete the task
    $('.table-responsive>table').on('confirm', '.trash', function () {
            var button = this;
            $.ajax({
                method: "POST",
                url: '/delTask',
                data: { task_id: $(button).data("taskid") }
            }).success(function () {
                reloadTasks();
            });
    });

    
    // change task
    $('.table-responsive>table').on('click', '.change', function () {
        var id = $(this).data("taskid");
        var text = $(this).closest('tr').find('.task_text').text();
        $('#c_task').text(text);

        $('.save').click(id, function () {
            
            var _task = $('#c_task').val();
            $.ajax({
                method: "POST",
                url: '/updateTask',
                data: {
                    task_id: id,
                    task: _task
                }
            }).success(function () {
                $('#myModal').modal('hide');
                //$('#c_task').val('');
                reloadTasks();
                $('.save').off('click');
            }).error(function () {
                $('.save').off('click');
            });
        });
    });
 
        // adds new task in today tasks
        $('#addTask').submit(function (e) {
            e.preventDefault();
            var _task = $('#task').val();
            var _date = $('#date').val();
            var _time = $('#time').val();
            var _priority = $('#priority').val();
            var _label_color = $('#color').val();
            var _label_text = $('#label_text').val();


            $.ajax({
                method: "POST",
                url: '/addTask',
                data: {
                    task: _task,
                    date: _date,
                    time: _time,
                    priority: _priority,
                    label_color: _label_color,
                    label_text: _label_text
                }
            }).success(function () {
                $('#addTask').find("input[type=text],input[type=time], textarea").val("");
                $('#newTask').collapse('hide');
                
                $('#color').colorselector();
                reloadTasks();
            });
        });

        // change password
        $('#change_password').submit(function (p) {
            p.preventDefault();
            var _password = $('#old_password').val();
            var _new_password = $('#new_password').val();
            var _con_password = $('#confirm_pas').val();
        
            $.ajax({
                method: "POST",
                url: '/changePas',
                data: {
                    password: _password,
                    new_password: _new_password,
                    confirm_pas: _con_password
                }
            }).success (function () {
                $('#c_password').collapse('hide');
                $('#change_password').find("input[type=password]").val("");
                $('.append_alert').append('<div class="alert alert-success alert-dismissible" role="alert" id="password_alert">\
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>\
                </button>Your password has been changed</div>');
            })
            .error(function () {
                $('#change_password').find("input[type=password]").val("");
                $('#c_password').collapse('hide');
                $('.append_alert').append('<div class="alert alert-danger alert-dismissible" role="alert" id="password_alert">\
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>\
                </button>Incorrect password</div>');
            });
           
        });
        reloadTasks();
        });