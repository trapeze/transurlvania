/*
*	MultiLang
*	Helper functions for MultiLang admin interface
*	
*	Requires jQuery library (http://www.jquery.com)
*	
*	Taylan Pince (tpince at trapeze dot com) - January 30, 2008
*/


$(function() {
    $("select[@name='_addtrans_lang']").change(function() {
        var index = this.selectedIndex;
        
        $("select[@name='_addtrans_lang']").each(function() {
            this.selectedIndex = index;
        });
    });
});