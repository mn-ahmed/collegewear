/** @odoo-module **/
import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';

/**
 * Menu item appended in the systray part of the navbar, redirects to the next
 * activities of all app
 */

var HelpWidget = Widget.extend({
   template: 'HelpSystray',
});
SystrayMenu.Items.push(HelpWidget);
export default HelpWidget;