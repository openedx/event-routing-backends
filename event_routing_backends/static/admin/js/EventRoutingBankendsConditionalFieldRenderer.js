(function($) {
    $(function() {
        function changeFieldsDisplay() {
          if($("#id_auth_scheme").val() == 'BASIC'){
                $('.field-auth_key').hide();
                $('.field-password').show();
                $('.field-username').show();
          }
          else{
                $('.field-auth_key').show();
                $('.field-password').hide();
                $('.field-username').hide();
          }
        }
        changeFieldsDisplay();
        $('#id_auth_scheme').on('change', function() {
          changeFieldsDisplay();
        });
    });
})(django.jQuery);
