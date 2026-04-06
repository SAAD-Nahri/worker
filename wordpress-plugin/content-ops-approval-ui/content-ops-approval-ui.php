<?php
/**
 * Plugin Name: Content Ops Approval UI
 * Description: Thin WordPress admin review shell for the Content Ops operator API.
 * Version: 0.1.0
 * Author: Codex
 */

if (! defined('ABSPATH')) {
    exit;
}

define('CONTENT_OPS_APPROVAL_UI_VERSION', '0.1.0');
define('CONTENT_OPS_APPROVAL_UI_FILE', __FILE__);
define('CONTENT_OPS_APPROVAL_UI_DIR', plugin_dir_path(__FILE__));
define('CONTENT_OPS_APPROVAL_UI_URL', plugin_dir_url(__FILE__));

require_once CONTENT_OPS_APPROVAL_UI_DIR . 'includes/class-content-ops-approval-ui.php';

function content_ops_approval_ui_bootstrap() {
    return Content_Ops_Approval_UI::instance();
}

content_ops_approval_ui_bootstrap();
