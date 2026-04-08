<?php

if (! defined('ABSPATH')) {
    exit;
}

class Content_Ops_Approval_UI {
    const OPTION_KEY = 'content_ops_approval_ui_settings';
    const REVIEW_CAPABILITY = 'edit_others_posts';
    const SETTINGS_CAPABILITY = 'manage_options';
    const NOTICE_TRANSIENT_PREFIX = 'content_ops_approval_notice_';

    private static $instance = null;

    public static function instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', array($this, 'register_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_assets'));
    }

    public function register_admin_menu() {
        add_menu_page(
            __('Content Ops Approval', 'content-ops-approval-ui'),
            __('Content Ops Approval', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-dashboard',
            array($this, 'render_dashboard_page'),
            'dashicons-yes-alt',
            59
        );

        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Dashboard', 'content-ops-approval-ui'),
            __('Dashboard', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-dashboard',
            array($this, 'render_dashboard_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Draft Review', 'content-ops-approval-ui'),
            __('Draft Review', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-drafts',
            array($this, 'render_drafts_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Social Review', 'content-ops-approval-ui'),
            __('Social Review', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-social',
            array($this, 'render_social_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Media Review', 'content-ops-approval-ui'),
            __('Media Review', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-media',
            array($this, 'render_media_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Queue Review', 'content-ops-approval-ui'),
            __('Queue Review', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-queue',
            array($this, 'render_queue_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Validation', 'content-ops-approval-ui'),
            __('Validation', 'content-ops-approval-ui'),
            self::REVIEW_CAPABILITY,
            'content-ops-approval-validation',
            array($this, 'render_validation_page')
        );
        add_submenu_page(
            'content-ops-approval-dashboard',
            __('Settings', 'content-ops-approval-ui'),
            __('Settings', 'content-ops-approval-ui'),
            self::SETTINGS_CAPABILITY,
            'content-ops-approval-settings',
            array($this, 'render_settings_page')
        );
    }

    public function register_settings() {
        register_setting(
            'content_ops_approval_ui',
            self::OPTION_KEY,
            array($this, 'sanitize_settings')
        );
    }

    public function sanitize_settings($input) {
        $input = is_array($input) ? $input : array();

        return array(
            'api_base_url' => esc_url_raw(isset($input['api_base_url']) ? $input['api_base_url'] : ''),
            'shared_secret' => sanitize_text_field(isset($input['shared_secret']) ? $input['shared_secret'] : ''),
        );
    }

    public function enqueue_assets($hook_suffix) {
        if (false === strpos((string) $hook_suffix, 'content-ops-approval')) {
            return;
        }

        wp_enqueue_style(
            'content-ops-approval-ui-admin',
            CONTENT_OPS_APPROVAL_UI_URL . 'assets/admin.css',
            array(),
            CONTENT_OPS_APPROVAL_UI_VERSION
        );
    }

    public function render_dashboard_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $payload = $this->api_request('GET', '/dashboard/summary');
        $this->render_page_open(__('Operator Dashboard', 'content-ops-approval-ui'));
        $this->render_notice();

        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_page_close();
            return;
        }

        echo '<div class="content-ops-dashboard-grid">';
        $this->render_metric_card(__('Draft Review', 'content-ops-approval-ui'), array(
            __('Pending review', 'content-ops-approval-ui') => $payload['drafts']['pending_review_count'],
            __('Needs edits', 'content-ops-approval-ui') => $payload['drafts']['needs_edits_count'],
            __('Approved forward', 'content-ops-approval-ui') => $payload['drafts']['approved_for_next_step_count'],
        ));
        $this->render_metric_card(__('Social Review', 'content-ops-approval-ui'), array(
            __('Pending review', 'content-ops-approval-ui') => $payload['social_packages']['pending_review_count'],
            __('Needs edits', 'content-ops-approval-ui') => $payload['social_packages']['needs_edits_count'],
            __('Approved for queue', 'content-ops-approval-ui') => $payload['social_packages']['approved_for_queue_count'],
        ));
        $this->render_metric_card(__('Media Review', 'content-ops-approval-ui'), array(
            __('Pending review', 'content-ops-approval-ui') => $payload['media_assets']['pending_review_count'],
            __('Needs edits', 'content-ops-approval-ui') => $payload['media_assets']['needs_edits_count'],
            __('Approved', 'content-ops-approval-ui') => $payload['media_assets']['approved_count'],
        ));
        $this->render_metric_card(__('Queue', 'content-ops-approval-ui'), array(
            __('Ready items', 'content-ops-approval-ui') => $payload['queue']['ready_items_count'],
            __('Schedule collisions', 'content-ops-approval-ui') => $payload['queue']['schedule_collision_count'],
        ));
        $this->render_metric_card(__('Transport', 'content-ops-approval-ui'), array(
            __('Failures', 'content-ops-approval-ui') => $payload['transport']['failure_count'],
            __('Activation signal', 'content-ops-approval-ui') => $payload['transport']['activation_signal'],
        ));
        echo '</div>';

        echo '<div class="content-ops-dashboard-grid">';
        $this->render_activity_list(
            __('Recent Review Activity', 'content-ops-approval-ui'),
            isset($payload['recent_activity']) ? $payload['recent_activity'] : array()
        );
        $this->render_alert_list(
            __('Current Alerts', 'content-ops-approval-ui'),
            isset($payload['current_alerts']) ? $payload['current_alerts'] : array()
        );
        echo '</div>';

        echo '<div class="content-ops-dashboard-grid">';
        $this->render_priority_review_list(
            __('Review Now: Drafts', 'content-ops-approval-ui'),
            isset($payload['priority_drafts']) ? $payload['priority_drafts'] : array(),
            'draft'
        );
        $this->render_priority_review_list(
            __('Review Now: Social Packages', 'content-ops-approval-ui'),
            isset($payload['priority_social_packages']) ? $payload['priority_social_packages'] : array(),
            'social_package'
        );
        $this->render_priority_review_list(
            __('Review Now: Media Assets', 'content-ops-approval-ui'),
            isset($payload['priority_media_assets']) ? $payload['priority_media_assets'] : array(),
            'media_asset'
        );
        $this->render_priority_review_list(
            __('Review Now: Queue', 'content-ops-approval-ui'),
            isset($payload['priority_queue_items']) ? $payload['priority_queue_items'] : array(),
            'queue_item'
        );
        echo '</div>';

        $this->render_fast_lane_card($payload['fast_lane']);
        $this->render_page_close();
    }

    public function render_drafts_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $this->handle_draft_submission();
        $filters = $this->get_draft_filters_from_request();
        $draft_id = isset($_GET['draft_id']) ? sanitize_text_field(wp_unslash($_GET['draft_id'])) : '';
        $payload = $draft_id
            ? $this->api_request('GET', '/drafts/' . rawurlencode($draft_id))
            : $this->api_request('GET', $this->build_api_path('/drafts/inbox', $filters));

        $this->render_page_open(__('Draft Review', 'content-ops-approval-ui'));
        $this->render_notice();
        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_page_close();
            return;
        }

        if ($draft_id) {
            $this->render_draft_detail($payload, $filters);
        } else {
            $this->render_draft_inbox($payload, $filters);
        }

        $this->render_page_close();
    }

    public function render_social_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $this->handle_social_submission();
        $filters = $this->get_social_filters_from_request();
        $social_package_id = isset($_GET['social_package_id']) ? sanitize_text_field(wp_unslash($_GET['social_package_id'])) : '';
        $payload = $social_package_id
            ? $this->api_request('GET', '/social-packages/' . rawurlencode($social_package_id))
            : $this->api_request('GET', $this->build_api_path('/social-packages/inbox', $filters));

        $this->render_page_open(__('Social Package Review', 'content-ops-approval-ui'));
        $this->render_notice();
        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_page_close();
            return;
        }

        if ($social_package_id) {
            $this->render_social_detail($payload, $filters);
        } else {
            $this->render_social_inbox($payload, $filters);
        }

        $this->render_page_close();
    }

    public function render_media_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $this->handle_media_submission();
        $filters = $this->get_media_filters_from_request();
        $asset_record_id = isset($_GET['asset_record_id']) ? sanitize_text_field(wp_unslash($_GET['asset_record_id'])) : '';
        $payload = $asset_record_id
            ? $this->api_request('GET', '/media-assets/' . rawurlencode($asset_record_id))
            : $this->api_request('GET', $this->build_api_path('/media-assets/inbox', $filters));

        $this->render_page_open(__('Media Asset Review', 'content-ops-approval-ui'));
        $this->render_notice();
        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_page_close();
            return;
        }

        if ($asset_record_id) {
            $this->render_media_detail($payload, $filters);
        } else {
            $this->render_media_inbox($payload, $filters);
        }

        $this->render_page_close();
    }

    public function render_queue_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $this->handle_queue_submission();
        $filters = $this->get_queue_filters_from_request();
        $queue_item_id = isset($_GET['queue_item_id']) ? sanitize_text_field(wp_unslash($_GET['queue_item_id'])) : '';
        $payload = $queue_item_id
            ? $this->api_request('GET', '/queue/' . rawurlencode($queue_item_id))
            : $this->api_request('GET', $this->build_api_path('/queue/inbox', $filters));

        $this->render_page_open(__('Queue Review', 'content-ops-approval-ui'));
        $this->render_notice();
        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_page_close();
            return;
        }

        if ($queue_item_id) {
            $this->render_queue_detail($payload, $filters);
        } else {
            $this->render_queue_inbox($payload, $filters);
        }

        $this->render_page_close();
    }

    public function render_settings_page() {
        if (! current_user_can(self::SETTINGS_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $settings = $this->get_settings();
        $api_base_url = $this->get_api_base_url();
        $this->render_page_open(__('Approval UI Settings', 'content-ops-approval-ui'));
        ?>
        <form method="post" action="options.php">
            <?php settings_fields('content_ops_approval_ui'); ?>
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row"><label for="content_ops_approval_ui_api_base_url"><?php esc_html_e('Operator API Base URL', 'content-ops-approval-ui'); ?></label></th>
                    <td>
                        <input class="regular-text" type="url" id="content_ops_approval_ui_api_base_url" name="<?php echo esc_attr(self::OPTION_KEY); ?>[api_base_url]" value="<?php echo esc_attr($settings['api_base_url']); ?>" placeholder="http://127.0.0.1:8765">
                        <p class="description"><?php esc_html_e('Use localhost only when WordPress and the operator API run on the same machine. For hosted WordPress, use a reachable HTTPS operator-API URL instead.', 'content-ops-approval-ui'); ?></p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="content_ops_approval_ui_shared_secret"><?php esc_html_e('Shared Secret', 'content-ops-approval-ui'); ?></label></th>
                    <td>
                        <input class="regular-text" type="password" id="content_ops_approval_ui_shared_secret" name="<?php echo esc_attr(self::OPTION_KEY); ?>[shared_secret]" value="<?php echo esc_attr($settings['shared_secret']); ?>">
                        <p class="description"><?php esc_html_e('This must match the shared secret configured for the Python operator API.', 'content-ops-approval-ui'); ?></p>
                    </td>
                </tr>
            </table>
            <?php submit_button(__('Save Settings', 'content-ops-approval-ui')); ?>
        </form>
        <?php
        $this->render_api_reachability_guidance($api_base_url);
        $this->render_page_close();
    }

    public function render_validation_page() {
        if (! current_user_can(self::REVIEW_CAPABILITY)) {
            wp_die(esc_html__('You do not have permission to access this page.', 'content-ops-approval-ui'));
        }

        $payload = $this->api_request('GET', '/validation/operator-baseline');
        $this->render_page_open(__('Approval UI Validation', 'content-ops-approval-ui'));
        $this->render_notice();

        if (is_wp_error($payload)) {
            $this->render_api_error($payload);
            $this->render_validation_local_checks(null);
            $this->render_page_close();
            return;
        }

        $this->render_validation_local_checks($payload);
        $this->render_validation_backend_checks($payload);
        $this->render_validation_manual_checklist();
        $this->render_page_close();
    }

    private function handle_draft_submission() {
        if ('POST' !== $_SERVER['REQUEST_METHOD']) {
            return;
        }
        if (! isset($_POST['content_ops_action']) || 'draft_review' !== sanitize_text_field(wp_unslash($_POST['content_ops_action']))) {
            return;
        }
        check_admin_referer('content_ops_approval_action');
        $draft_id = sanitize_text_field(wp_unslash($_POST['draft_id']));
        $outcome = sanitize_text_field(wp_unslash($_POST['review_outcome']));
        $note = sanitize_textarea_field(wp_unslash(isset($_POST['review_note']) ? $_POST['review_note'] : ''));
        $selected_variant = sanitize_text_field(wp_unslash(isset($_POST['selected_headline_variant']) ? $_POST['selected_headline_variant'] : ''));
        $current_headline = sanitize_text_field(wp_unslash(isset($_POST['current_headline_selected']) ? $_POST['current_headline_selected'] : ''));

        if ('needs_edits' === $outcome && ! $this->has_actionable_note($note)) {
            $this->store_result_notice(
                new WP_Error(
                    'content_ops_actionable_note_required',
                    __('Needs Edits requires a short actionable note.', 'content-ops-approval-ui')
                ),
                ''
            );
            $this->redirect_back();
        }

        if ($selected_variant && $selected_variant !== $current_headline) {
            $variant_response = $this->api_request('POST', '/drafts/' . rawurlencode($draft_id) . '/select-headline-variant', array(
                'headline_variant' => $selected_variant,
            ));
            if (is_wp_error($variant_response)) {
                $this->store_result_notice($variant_response, '');
                $this->redirect_back();
            }
        }

        $response = $this->api_request('POST', '/drafts/' . rawurlencode($draft_id) . '/review', array(
            'review_outcome' => $outcome,
            'review_notes' => $note ? array($note) : array(),
            'reviewer_label' => $this->get_operator_label(),
        ));
        $this->store_result_notice($response, __('Draft review saved.', 'content-ops-approval-ui'));
        $this->redirect_back();
    }

    private function handle_social_submission() {
        if ('POST' !== $_SERVER['REQUEST_METHOD']) {
            return;
        }
        if (! isset($_POST['content_ops_action']) || 'social_review' !== sanitize_text_field(wp_unslash($_POST['content_ops_action']))) {
            return;
        }
        check_admin_referer('content_ops_approval_action');
        $social_package_id = sanitize_text_field(wp_unslash($_POST['social_package_id']));
        $outcome = sanitize_text_field(wp_unslash($_POST['review_outcome']));
        $note = sanitize_textarea_field(wp_unslash(isset($_POST['review_note']) ? $_POST['review_note'] : ''));
        $selected_variant_label = sanitize_text_field(wp_unslash(isset($_POST['selected_variant_label']) ? $_POST['selected_variant_label'] : ''));
        $current_variant_label = sanitize_text_field(wp_unslash(isset($_POST['current_variant_label']) ? $_POST['current_variant_label'] : ''));

        if ('needs_edits' === $outcome && ! $this->has_actionable_note($note)) {
            $this->store_result_notice(
                new WP_Error(
                    'content_ops_actionable_note_required',
                    __('Needs Edits requires a short actionable note.', 'content-ops-approval-ui')
                ),
                ''
            );
            $this->redirect_back();
        }

        if ($selected_variant_label && $selected_variant_label !== $current_variant_label) {
            $variant_response = $this->api_request('POST', '/social-packages/' . rawurlencode($social_package_id) . '/select-variant', array(
                'variant_label' => $selected_variant_label,
            ));
            if (is_wp_error($variant_response)) {
                $this->store_result_notice($variant_response, '');
                $this->redirect_back();
            }
        }

        $response = $this->api_request('POST', '/social-packages/' . rawurlencode($social_package_id) . '/review', array(
            'review_outcome' => $outcome,
            'review_notes' => $note ? array($note) : array(),
            'reviewer_label' => $this->get_operator_label(),
        ));
        $this->store_result_notice($response, __('Social package review saved.', 'content-ops-approval-ui'));
        $this->redirect_back();
    }

    private function handle_queue_submission() {
        if ('POST' !== $_SERVER['REQUEST_METHOD']) {
            return;
        }
        if (! isset($_POST['content_ops_action'])) {
            return;
        }
        check_admin_referer('content_ops_approval_action');
        $action = sanitize_text_field(wp_unslash($_POST['content_ops_action']));
        $queue_item_id = sanitize_text_field(wp_unslash($_POST['queue_item_id']));

        if ('queue_review' === $action) {
            $outcome = sanitize_text_field(wp_unslash($_POST['review_outcome']));
            $note = sanitize_textarea_field(wp_unslash(isset($_POST['review_note']) ? $_POST['review_note'] : ''));
            if (in_array($outcome, array('hold', 'removed'), true) && ! $this->has_actionable_note($note)) {
                $this->store_result_notice(
                    new WP_Error(
                        'content_ops_actionable_note_required',
                        __('This queue action requires a short actionable note.', 'content-ops-approval-ui')
                    ),
                    ''
                );
                $this->redirect_back();
            }
            $response = $this->api_request('POST', '/queue/' . rawurlencode($queue_item_id) . '/approve', array(
                'review_outcome' => $outcome,
                'review_notes' => $note ? array($note) : array(),
                'reviewer_label' => $this->get_operator_label(),
            ));
            $this->store_result_notice($response, __('Queue review saved.', 'content-ops-approval-ui'));
            $this->redirect_back();
        }

        if ('queue_schedule' === $action) {
            $scheduled_for = sanitize_text_field(wp_unslash(isset($_POST['scheduled_for']) ? $_POST['scheduled_for'] : ''));
            $timestamp = $scheduled_for ? strtotime($scheduled_for) : false;
            if ($timestamp) {
                $scheduled_for = gmdate('c', $timestamp);
            }
            $response = $this->api_request('POST', '/queue/' . rawurlencode($queue_item_id) . '/schedule', array(
                'scheduled_for' => $scheduled_for,
                'reviewer_label' => $this->get_operator_label(),
                'schedule_mode' => 'manual',
            ));
            $this->store_result_notice($response, __('Queue schedule recorded.', 'content-ops-approval-ui'));
            $this->redirect_back();
        }
    }

    private function handle_media_submission() {
        if ('POST' !== $_SERVER['REQUEST_METHOD']) {
            return;
        }
        if (! isset($_POST['content_ops_action']) || 'media_review' !== sanitize_text_field(wp_unslash($_POST['content_ops_action']))) {
            return;
        }
        check_admin_referer('content_ops_approval_action');
        $asset_record_id = sanitize_text_field(wp_unslash($_POST['asset_record_id']));
        $outcome = sanitize_text_field(wp_unslash($_POST['review_outcome']));
        $note = sanitize_textarea_field(wp_unslash(isset($_POST['review_note']) ? $_POST['review_note'] : ''));

        if (in_array($outcome, array('needs_edits', 'rejected'), true) && ! $this->has_actionable_note($note)) {
            $this->store_result_notice(
                new WP_Error(
                    'content_ops_actionable_note_required',
                    __('Media review needs a short actionable note for Needs Edits or Reject.', 'content-ops-approval-ui')
                ),
                ''
            );
            $this->redirect_back();
        }

        $response = $this->api_request('POST', '/media-assets/' . rawurlencode($asset_record_id) . '/review', array(
            'review_outcome' => $outcome,
            'review_notes' => $note ? array($note) : array(),
            'reviewer_label' => $this->get_operator_label(),
        ));
        $this->store_result_notice($response, __('Media asset review saved.', 'content-ops-approval-ui'));
        $this->redirect_back();
    }

    private function render_draft_inbox($payload, $filters) {
        $this->render_draft_filter_bar($filters);
        echo '<p class="content-ops-muted">' . esc_html__('Human review remains required. Fast-lane scoring is visible later but disabled in this version.', 'content-ops-approval-ui') . '</p>';
        echo '<table class="widefat striped"><thead><tr>';
        echo '<th>' . esc_html__('Draft', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Source Kind', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Template', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Category', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Quality', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Derivative Risk', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Routing', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Approval', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Actions', 'content-ops-approval-ui') . '</th>';
        echo '</tr></thead><tbody>';

        foreach ($payload['rows'] as $row) {
            $detail_url = $this->build_admin_page_url(
                'content-ops-approval-drafts',
                array('draft_id' => $row['draft_id']),
                $this->get_draft_filter_keys()
            );
            echo '<tr>';
            echo '<td><strong>' . esc_html($row['draft_id']) . '</strong><br><span class="content-ops-muted">' . esc_html($row['source_item_id']) . '</span><br><span class="content-ops-muted">' . esc_html($row['operator_signal']) . '</span></td>';
            echo '<td>' . esc_html($row['source_domain']) . '</td>';
            echo '<td>' . esc_html($row['template_id']) . '</td>';
            echo '<td>' . esc_html($row['category']) . '</td>';
            echo '<td>' . esc_html($row['quality_gate_status']) . '</td>';
            echo '<td>' . esc_html($row['derivative_risk_level']) . '</td>';
            echo '<td>' . esc_html($row['routing_action']) . '</td>';
            echo '<td>' . esc_html($row['approval_state']) . '</td>';
            echo '<td class="content-ops-inline-actions">';
            echo '<a class="button" href="' . esc_url($detail_url) . '">' . esc_html__('Open Detail', 'content-ops-approval-ui') . '</a>';
            $this->render_inline_review_form('draft_review', 'draft_id', $row['draft_id'], 'approved', '');
            $this->render_inline_note_review_form('draft_review', 'draft_id', $row['draft_id'], 'needs_edits', __('Needs Edits', 'content-ops-approval-ui'));
            echo '</td>';
            echo '</tr>';
        }

        echo '</tbody></table>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_social_inbox($payload, $filters) {
        $this->render_social_filter_bar($filters);
        echo '<table class="widefat striped"><thead><tr>';
        echo '<th>' . esc_html__('Blog Title', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Hook', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Caption', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('CTA', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Variant', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Approval', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Linkage', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Actions', 'content-ops-approval-ui') . '</th>';
        echo '</tr></thead><tbody>';
        foreach ($payload['rows'] as $row) {
            $detail_url = $this->build_admin_page_url(
                'content-ops-approval-social',
                array('social_package_id' => $row['social_package_id']),
                $this->get_social_filter_keys()
            );
            echo '<tr>';
            echo '<td><strong>' . esc_html((string) $row['linked_blog_title']) . '</strong><br><span class="content-ops-muted">' . esc_html((string) $row['social_package_id']) . '</span></td>';
            echo '<td>' . esc_html($row['hook_text']) . '</td>';
            echo '<td>' . esc_html($row['caption_text']) . '</td>';
            echo '<td>' . esc_html($row['comment_cta_text']) . '</td>';
            echo '<td>' . esc_html((string) $row['selected_variant_label']) . '</td>';
            echo '<td>' . esc_html($row['approval_state']) . '</td>';
            echo '<td>' . esc_html($row['linkage_state']) . '</td>';
            echo '<td class="content-ops-inline-actions">';
            echo '<a class="button" href="' . esc_url($detail_url) . '">' . esc_html__('Open Detail', 'content-ops-approval-ui') . '</a>';
            $this->render_inline_review_form('social_review', 'social_package_id', $row['social_package_id'], 'approved', '');
            $this->render_inline_note_review_form('social_review', 'social_package_id', $row['social_package_id'], 'needs_edits', __('Needs Edits', 'content-ops-approval-ui'));
            echo '</td>';
            echo '</tr>';
        }
        echo '</tbody></table>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_media_inbox($payload, $filters) {
        $this->render_media_filter_bar($filters);
        echo '<p class="content-ops-muted">' . esc_html__('This screen is for review-safe asset approval only. Media generation and upload still stay outside WordPress admin in this phase.', 'content-ops-approval-ui') . '</p>';
        echo '<table class="widefat striped"><thead><tr>';
        echo '<th>' . esc_html__('Asset', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Source', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Usage', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Readiness', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Provenance', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Approval', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Actions', 'content-ops-approval-ui') . '</th>';
        echo '</tr></thead><tbody>';
        foreach ($payload['rows'] as $row) {
            $detail_url = $this->build_admin_page_url(
                'content-ops-approval-media',
                array('asset_record_id' => $row['asset_record_id']),
                $this->get_media_filter_keys()
            );
            echo '<tr>';
            $asset_title = ! empty($row['linked_blog_title']) ? (string) $row['linked_blog_title'] : (string) $row['asset_record_id'];
            echo '<td><strong>' . esc_html($asset_title) . '</strong><br><span class="content-ops-muted">' . esc_html((string) $row['asset_record_id']) . '</span><br><span class="content-ops-muted">' . esc_html((string) $row['asset_url_or_path']) . '</span></td>';
            echo '<td>' . esc_html((string) $row['asset_source_kind']) . '</td>';
            echo '<td>' . esc_html((string) $row['intended_usage']) . '</td>';
            echo '<td>';
            echo ! empty($row['asset_complete'])
                ? esc_html__('Ready', 'content-ops-approval-ui')
                : esc_html__('Blocked', 'content-ops-approval-ui');
            if (! empty($row['asset_block_reason'])) {
                echo '<br><span class="content-ops-muted">' . esc_html((string) $row['asset_block_reason']) . '</span>';
            }
            echo '</td>';
            echo '<td>' . esc_html((string) $row['provenance_reference']) . '</td>';
            echo '<td>' . esc_html((string) $row['approval_state']) . '</td>';
            echo '<td class="content-ops-inline-actions">';
            echo '<a class="button" href="' . esc_url($detail_url) . '">' . esc_html__('Open Detail', 'content-ops-approval-ui') . '</a>';
            $this->render_inline_review_form('media_review', 'asset_record_id', $row['asset_record_id'], 'approved', '');
            $this->render_inline_note_review_form('media_review', 'asset_record_id', $row['asset_record_id'], 'needs_edits', __('Needs Edits', 'content-ops-approval-ui'));
            echo '</td>';
            echo '</tr>';
        }
        echo '</tbody></table>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_queue_inbox($payload, $filters) {
        $this->render_queue_filter_bar($filters);
        echo '<table class="widefat striped"><thead><tr>';
        echo '<th>' . esc_html__('Title', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Queue Type', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Queue State', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Queue Review', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Scheduled For', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Warnings', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Actions', 'content-ops-approval-ui') . '</th>';
        echo '</tr></thead><tbody>';
        foreach ($payload['rows'] as $row) {
            $detail_url = $this->build_admin_page_url(
                'content-ops-approval-queue',
                array('queue_item_id' => $row['queue_item_id']),
                $this->get_queue_filter_keys()
            );
            echo '<tr>';
            echo '<td><strong>' . esc_html((string) $row['title']) . '</strong><br><span class="content-ops-muted">' . esc_html((string) $row['queue_item_id']) . '</span></td>';
            echo '<td>' . esc_html($row['queue_type']) . '</td>';
            echo '<td>' . esc_html($row['queue_state']) . '</td>';
            echo '<td>' . esc_html($row['queue_review_state']) . '</td>';
            echo '<td>' . esc_html((string) $row['scheduled_for']) . '</td>';
            echo '<td>';
            echo esc_html(implode(', ', $row['collision_warnings']));
            if (! empty($row['approve_block_reason'])) {
                echo '<br><span class="content-ops-muted">' . esc_html($row['approve_block_reason']) . '</span>';
            }
            if (! empty($row['schedule_block_reason'])) {
                echo '<br><span class="content-ops-muted">' . esc_html($row['schedule_block_reason']) . '</span>';
            }
            echo '</td>';
            echo '<td class="content-ops-inline-actions">';
            echo '<a class="button" href="' . esc_url($detail_url) . '">' . esc_html__('Open Detail', 'content-ops-approval-ui') . '</a>';
            if (! empty($row['approve_allowed'])) {
                $this->render_inline_review_form('queue_review', 'queue_item_id', $row['queue_item_id'], 'approved', '');
            }
            $this->render_inline_note_review_form('queue_review', 'queue_item_id', $row['queue_item_id'], 'hold', __('Hold', 'content-ops-approval-ui'));
            if ('blog_publish' === $row['queue_type'] && ! empty($row['schedule_allowed'])) {
                echo '<a class="button button-secondary" href="' . esc_url($detail_url) . '">' . esc_html__('Set Schedule', 'content-ops-approval-ui') . '</a>';
            }
            echo '</td>';
            echo '</tr>';
        }
        echo '</tbody></table>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_draft_detail($payload, $filters) {
        $draft = $payload['draft'];
        $back_url = $this->build_admin_page_url(
            'content-ops-approval-drafts',
            array(),
            $this->get_draft_filter_keys()
        );
        echo '<a class="button" href="' . esc_url($back_url) . '">' . esc_html__('Back to Draft Inbox', 'content-ops-approval-ui') . '</a>';
        echo '<div class="content-ops-review-layout">';
        echo '<div class="content-ops-preview"><h2>' . esc_html($draft['headline_selected']) . '</h2>';
        echo '<p>' . esc_html($draft['intro_text']) . '</p>';
        foreach ($draft['sections'] as $section) {
            echo '<section><h3>' . esc_html($section['section_label']) . '</h3>';
            foreach ($section['body_blocks'] as $block) {
                echo '<p>' . esc_html($block) . '</p>';
            }
            if (! empty($section['bullet_points'])) {
                echo '<ul>';
                foreach ($section['bullet_points'] as $point) {
                    echo '<li>' . esc_html($point) . '</li>';
                }
                echo '</ul>';
            }
            echo '</section>';
        }
        if (! empty($draft['excerpt'])) {
            echo '<p><strong>' . esc_html__('Excerpt:', 'content-ops-approval-ui') . '</strong> ' . esc_html($draft['excerpt']) . '</p>';
        }
        if (! empty($draft['headline_variants'])) {
            echo '<h3>' . esc_html__('Headline Suggestions', 'content-ops-approval-ui') . '</h3>';
            echo '<ul>';
            foreach ($draft['headline_variants'] as $variant) {
                echo '<li>' . esc_html($variant) . '</li>';
            }
            echo '</ul>';
        }
        echo '</div>';
        echo '<aside class="content-ops-sidebar">';
        $this->render_meta_list(array(
            __('Source Title', 'content-ops-approval-ui') => $payload['source_lineage']['source_title'],
            __('Source Domain', 'content-ops-approval-ui') => $payload['source_lineage']['source_domain'],
            __('Source Published', 'content-ops-approval-ui') => $payload['source_lineage']['source_published_at'],
            __('Template', 'content-ops-approval-ui') => $draft['template_id'],
            __('Category', 'content-ops-approval-ui') => $draft['category'],
            __('Quality Gate', 'content-ops-approval-ui') => $draft['quality_gate_status'],
            __('Derivative Risk', 'content-ops-approval-ui') => $draft['derivative_risk_level'],
            __('Approval State', 'content-ops-approval-ui') => $draft['approval_state'],
            __('Blog Publish ID', 'content-ops-approval-ui') => isset($payload['downstream']['blog_publish_id']) ? $payload['downstream']['blog_publish_id'] : '',
            __('Social Package ID', 'content-ops-approval-ui') => isset($payload['downstream']['social_package_id']) ? $payload['downstream']['social_package_id'] : '',
            __('Media Brief ID', 'content-ops-approval-ui') => isset($payload['downstream']['media_brief_id']) ? $payload['downstream']['media_brief_id'] : '',
            __('Asset Record ID', 'content-ops-approval-ui') => isset($payload['downstream']['asset_record_id']) ? $payload['downstream']['asset_record_id'] : '',
            __('Asset Readiness', 'content-ops-approval-ui') => ! empty($payload['downstream']['asset_complete']) ? __('Ready', 'content-ops-approval-ui') : __('Blocked', 'content-ops-approval-ui'),
        ));
        if (! empty($payload['downstream']['asset_block_reason'])) {
            echo '<p class="content-ops-muted">' . esc_html((string) $payload['downstream']['asset_block_reason']) . '</p>';
        }
        if (! empty($payload['source_lineage']['source_url'])) {
            $this->render_link_block(
                __('Source URL', 'content-ops-approval-ui'),
                $payload['source_lineage']['source_url'],
                __('Open Source', 'content-ops-approval-ui')
            );
        }
        if (! empty($payload['linked_asset'])) {
            echo '<p><a class="button button-secondary" href="' . esc_url($this->build_admin_page_url('content-ops-approval-media', array('asset_record_id' => $payload['linked_asset']['asset_record_id']))) . '">' . esc_html__('Open Linked Asset', 'content-ops-approval-ui') . '</a></p>';
        }
        $this->render_ai_assistance_log(
            __('Draft AI Usage', 'content-ops-approval-ui'),
            isset($draft['ai_assistance_log']) ? $draft['ai_assistance_log'] : array()
        );
        $this->render_draft_detail_review_form($draft);
        $this->render_history_list($payload['review_history']);
        echo '</aside></div>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_social_detail($payload, $filters) {
        $package = $payload['social_package'];
        $back_url = $this->build_admin_page_url(
            'content-ops-approval-social',
            array(),
            $this->get_social_filter_keys()
        );
        echo '<a class="button" href="' . esc_url($back_url) . '">' . esc_html__('Back to Social Inbox', 'content-ops-approval-ui') . '</a>';
        echo '<div class="content-ops-review-layout">';
        echo '<div class="content-ops-preview">';
        echo '<h2>' . esc_html__('Social Package Preview', 'content-ops-approval-ui') . '</h2>';
        echo '<p><strong>' . esc_html__('Hook', 'content-ops-approval-ui') . ':</strong> ' . esc_html($package['hook_text']) . '</p>';
        echo '<p><strong>' . esc_html__('Caption', 'content-ops-approval-ui') . ':</strong> ' . esc_html($package['caption_text']) . '</p>';
        echo '<p><strong>' . esc_html__('Comment CTA', 'content-ops-approval-ui') . ':</strong> ' . esc_html($package['comment_cta_text']) . '</p>';
        if (! empty($payload['linked_blog_publish'])) {
            echo '<h3>' . esc_html__('Linked Blog', 'content-ops-approval-ui') . '</h3>';
            echo '<p>' . esc_html($payload['linked_blog_publish']['wordpress_title']) . '</p>';
            if (! empty($payload['linked_blog_publish']['wordpress_post_url'])) {
                echo '<p><a href="' . esc_url($payload['linked_blog_publish']['wordpress_post_url']) . '" target="_blank" rel="noopener noreferrer">' . esc_html__('Open Blog URL', 'content-ops-approval-ui') . '</a></p>';
            }
        }
        if (! empty($payload['linked_draft'])) {
            echo '<h3>' . esc_html__('Linked Draft', 'content-ops-approval-ui') . '</h3>';
            echo '<p><strong>' . esc_html__('Headline', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_draft']['headline_selected']) . '</p>';
            if (! empty($payload['linked_draft']['excerpt'])) {
                echo '<p><strong>' . esc_html__('Excerpt', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_draft']['excerpt']) . '</p>';
            }
        }
        echo '</div><aside class="content-ops-sidebar">';
        $this->render_meta_list(array(
            __('Approval State', 'content-ops-approval-ui') => $package['approval_state'],
            __('Package Template', 'content-ops-approval-ui') => $package['package_template_id'],
            __('Comment Template', 'content-ops-approval-ui') => $package['comment_template_id'],
            __('Variant', 'content-ops-approval-ui') => $package['selected_variant_label'],
            __('Draft Template', 'content-ops-approval-ui') => ! empty($payload['linked_draft']) ? $payload['linked_draft']['template_id'] : '',
            __('Draft Category', 'content-ops-approval-ui') => ! empty($payload['linked_draft']) ? $payload['linked_draft']['category'] : '',
            __('Blog Publish ID', 'content-ops-approval-ui') => ! empty($payload['linked_blog_publish']) ? $payload['linked_blog_publish']['blog_publish_id'] : '',
            __('Asset Record ID', 'content-ops-approval-ui') => ! empty($payload['linked_asset']) ? $payload['linked_asset']['asset_record_id'] : '',
            __('Asset Readiness', 'content-ops-approval-ui') => ! empty($payload['asset_readiness']['asset_complete']) ? __('Ready', 'content-ops-approval-ui') : __('Blocked', 'content-ops-approval-ui'),
        ));
        if (! empty($payload['asset_readiness']['asset_block_reason'])) {
            echo '<p class="content-ops-muted">' . esc_html((string) $payload['asset_readiness']['asset_block_reason']) . '</p>';
        }
        if (! empty($payload['linked_asset'])) {
            echo '<p><a class="button button-secondary" href="' . esc_url($this->build_admin_page_url('content-ops-approval-media', array('asset_record_id' => $payload['linked_asset']['asset_record_id']))) . '">' . esc_html__('Open Linked Asset', 'content-ops-approval-ui') . '</a></p>';
        }
        $this->render_ai_assistance_log(
            __('Social AI Usage', 'content-ops-approval-ui'),
            isset($package['ai_assistance_log']) ? $package['ai_assistance_log'] : array()
        );
        $this->render_ai_assistance_log(
            __('Linked Draft AI Usage', 'content-ops-approval-ui'),
            ! empty($payload['linked_draft']) && isset($payload['linked_draft']['ai_assistance_log'])
                ? $payload['linked_draft']['ai_assistance_log']
                : array()
        );
        $this->render_social_detail_review_form($package);
        $this->render_history_list($payload['review_history']);
        echo '</aside></div>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_media_detail($payload, $filters) {
        $asset = $payload['asset_record'];
        $back_url = $this->build_admin_page_url(
            'content-ops-approval-media',
            array(),
            $this->get_media_filter_keys()
        );
        echo '<a class="button" href="' . esc_url($back_url) . '">' . esc_html__('Back to Media Inbox', 'content-ops-approval-ui') . '</a>';
        echo '<div class="content-ops-review-layout">';
        echo '<div class="content-ops-preview">';
        echo '<h2>' . esc_html__('Media Asset Detail', 'content-ops-approval-ui') . '</h2>';
        echo '<p><strong>' . esc_html__('Asset path or URL', 'content-ops-approval-ui') . ':</strong> ' . esc_html($asset['asset_url_or_path']) . '</p>';
        echo '<p><strong>' . esc_html__('Alt text', 'content-ops-approval-ui') . ':</strong> ' . esc_html($asset['alt_text']) . '</p>';
        if (! empty($asset['caption_support_text'])) {
            echo '<p><strong>' . esc_html__('Caption support', 'content-ops-approval-ui') . ':</strong> ' . esc_html($asset['caption_support_text']) . '</p>';
        }
        if ($this->is_http_url(isset($asset['asset_url_or_path']) ? $asset['asset_url_or_path'] : '')) {
            echo '<p><a class="button button-secondary" href="' . esc_url($asset['asset_url_or_path']) . '" target="_blank" rel="noopener noreferrer">' . esc_html__('Open Asset', 'content-ops-approval-ui') . '</a></p>';
        }
        if (! empty($payload['linked_media_brief'])) {
            echo '<h3>' . esc_html__('Linked Media Brief', 'content-ops-approval-ui') . '</h3>';
            echo '<p><strong>' . esc_html__('Goal', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_media_brief']['brief_goal']) . '</p>';
            echo '<p><strong>' . esc_html__('Subject focus', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_media_brief']['subject_focus']) . '</p>';
            echo '<p><strong>' . esc_html__('Alt text seed', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_media_brief']['alt_text_seed']) . '</p>';
            if (! empty($payload['linked_media_brief']['visual_style_notes'])) {
                echo '<p><strong>' . esc_html__('Style notes', 'content-ops-approval-ui') . ':</strong> ' . esc_html(implode(', ', $payload['linked_media_brief']['visual_style_notes'])) . '</p>';
            }
            if (! empty($payload['linked_media_brief']['prohibited_visual_patterns'])) {
                echo '<p><strong>' . esc_html__('Avoid', 'content-ops-approval-ui') . ':</strong> ' . esc_html(implode(', ', $payload['linked_media_brief']['prohibited_visual_patterns'])) . '</p>';
            }
        }
        if (! empty($payload['linked_blog_publish'])) {
            echo '<h3>' . esc_html__('Linked Blog', 'content-ops-approval-ui') . '</h3>';
            echo '<p>' . esc_html($payload['linked_blog_publish']['wordpress_title']) . '</p>';
            if (! empty($payload['linked_blog_publish']['wordpress_post_url'])) {
                echo '<p><a href="' . esc_url($payload['linked_blog_publish']['wordpress_post_url']) . '" target="_blank" rel="noopener noreferrer">' . esc_html__('Open Blog URL', 'content-ops-approval-ui') . '</a></p>';
            }
        }
        if (! empty($payload['linked_social_package'])) {
            echo '<h3>' . esc_html__('Linked Social Package', 'content-ops-approval-ui') . '</h3>';
            echo '<p><strong>' . esc_html__('Hook', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_social_package']['hook_text']) . '</p>';
            echo '<p><strong>' . esc_html__('Caption', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_social_package']['caption_text']) . '</p>';
        }
        echo '</div><aside class="content-ops-sidebar">';
        $this->render_meta_list(array(
            __('Approval State', 'content-ops-approval-ui') => $asset['approval_state'],
            __('Asset Source', 'content-ops-approval-ui') => $asset['asset_source_kind'],
            __('Intended Usage', 'content-ops-approval-ui') => $asset['intended_usage'],
            __('Readiness', 'content-ops-approval-ui') => ! empty($payload['asset_readiness']['asset_complete']) ? __('Ready', 'content-ops-approval-ui') : __('Blocked', 'content-ops-approval-ui'),
            __('Block Reason', 'content-ops-approval-ui') => isset($payload['asset_readiness']['asset_block_reason']) ? $payload['asset_readiness']['asset_block_reason'] : '',
            __('Draft ID', 'content-ops-approval-ui') => isset($payload['linked_draft']['draft_id']) ? $payload['linked_draft']['draft_id'] : '',
            __('Blog Publish ID', 'content-ops-approval-ui') => ! empty($payload['linked_blog_publish']) ? $payload['linked_blog_publish']['blog_publish_id'] : '',
            __('Social Package ID', 'content-ops-approval-ui') => ! empty($payload['linked_social_package']) ? $payload['linked_social_package']['social_package_id'] : '',
            __('Media Brief ID', 'content-ops-approval-ui') => $asset['media_brief_id'],
        ));
        if (! empty($payload['linked_draft'])) {
            echo '<p><a class="button button-secondary" href="' . esc_url($this->build_admin_page_url('content-ops-approval-drafts', array('draft_id' => $payload['linked_draft']['draft_id']))) . '">' . esc_html__('Open Linked Draft', 'content-ops-approval-ui') . '</a></p>';
        }
        if (! empty($payload['linked_social_package'])) {
            echo '<p><a class="button button-secondary" href="' . esc_url($this->build_admin_page_url('content-ops-approval-social', array('social_package_id' => $payload['linked_social_package']['social_package_id']))) . '">' . esc_html__('Open Linked Social Package', 'content-ops-approval-ui') . '</a></p>';
        }
        $this->render_review_form('media_review', 'asset_record_id', $asset['asset_record_id']);
        $this->render_history_list($payload['review_history']);
        echo '</aside></div>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_queue_detail($payload, $filters) {
        $queue_item = $payload['queue_item'];
        $back_url = $this->build_admin_page_url(
            'content-ops-approval-queue',
            array(),
            $this->get_queue_filter_keys()
        );
        echo '<a class="button" href="' . esc_url($back_url) . '">' . esc_html__('Back to Queue Inbox', 'content-ops-approval-ui') . '</a>';
        echo '<div class="content-ops-review-layout">';
        echo '<div class="content-ops-preview">';
        echo '<h2>' . esc_html__('Queue Detail', 'content-ops-approval-ui') . '</h2>';
        if (! empty($payload['linked_blog_publish'])) {
            echo '<p><strong>' . esc_html__('Blog Title', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_blog_publish']['wordpress_title']) . '</p>';
        }
        if (! empty($payload['linked_social_package'])) {
            echo '<p><strong>' . esc_html__('Social Hook', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_social_package']['hook_text']) . '</p>';
        }
        echo '<p><strong>' . esc_html__('Queue State', 'content-ops-approval-ui') . ':</strong> ' . esc_html($queue_item['queue_state']) . '</p>';
        echo '<p><strong>' . esc_html__('Human Queue Review', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['queue_review_state']) . '</p>';
        echo '<p><strong>' . esc_html__('Schedule Signal', 'content-ops-approval-ui') . ':</strong> ' . esc_html((string) $payload['schedule_context']['signal']) . '</p>';
        echo '<p><strong>' . esc_html__('Collision Alerts', 'content-ops-approval-ui') . ':</strong> ' . esc_html(implode(', ', $payload['schedule_context']['alerts'])) . '</p>';
        if (! empty($payload['linked_mapping'])) {
            echo '<h3>' . esc_html__('Linked Mapping', 'content-ops-approval-ui') . '</h3>';
            echo '<p><strong>' . esc_html__('Mapping Status', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_mapping']['mapping_status']) . '</p>';
            if (! empty($payload['linked_mapping']['selected_hook_text'])) {
                echo '<p><strong>' . esc_html__('Selected Hook', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_mapping']['selected_hook_text']) . '</p>';
            }
            if (! empty($payload['linked_mapping']['selected_caption_text'])) {
                echo '<p><strong>' . esc_html__('Selected Caption', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_mapping']['selected_caption_text']) . '</p>';
            }
            if (! empty($payload['linked_mapping']['selected_comment_cta_text'])) {
                echo '<p><strong>' . esc_html__('Selected Comment CTA', 'content-ops-approval-ui') . ':</strong> ' . esc_html($payload['linked_mapping']['selected_comment_cta_text']) . '</p>';
            }
        }
        echo '</div><aside class="content-ops-sidebar">';
        $this->render_meta_list(array(
            __('Queue Type', 'content-ops-approval-ui') => $queue_item['queue_type'],
            __('Approval State', 'content-ops-approval-ui') => $queue_item['approval_state'],
            __('Approve Allowed', 'content-ops-approval-ui') => ! empty($payload['allowed_actions']['approve']) ? __('Yes', 'content-ops-approval-ui') : __('No', 'content-ops-approval-ui'),
            __('Schedule Allowed', 'content-ops-approval-ui') => ! empty($payload['allowed_actions']['schedule']) ? __('Yes', 'content-ops-approval-ui') : __('No', 'content-ops-approval-ui'),
            __('Scheduled For', 'content-ops-approval-ui') => $queue_item['scheduled_for'],
            __('Blog Publish ID', 'content-ops-approval-ui') => $queue_item['blog_publish_id'],
            __('Social Package ID', 'content-ops-approval-ui') => $queue_item['social_package_id'],
            __('Mapping ID', 'content-ops-approval-ui') => ! empty($payload['linked_mapping']) ? $payload['linked_mapping']['mapping_id'] : '',
            __('Asset Record ID', 'content-ops-approval-ui') => ! empty($payload['linked_asset']) ? $payload['linked_asset']['asset_record_id'] : '',
            __('Asset Readiness', 'content-ops-approval-ui') => ! empty($payload['asset_readiness']['asset_complete']) ? __('Ready', 'content-ops-approval-ui') : __('Blocked', 'content-ops-approval-ui'),
        ));
        if (! empty($payload['asset_readiness']['asset_block_reason'])) {
            echo '<p class="content-ops-muted">' . esc_html((string) $payload['asset_readiness']['asset_block_reason']) . '</p>';
        }
        if (! empty($payload['linked_asset'])) {
            echo '<p><a class="button button-secondary" href="' . esc_url($this->build_admin_page_url('content-ops-approval-media', array('asset_record_id' => $payload['linked_asset']['asset_record_id']))) . '">' . esc_html__('Open Linked Asset', 'content-ops-approval-ui') . '</a></p>';
        }
        if (! empty($payload['allowed_actions']['approve']) || ! empty($payload['allowed_actions']['hold']) || ! empty($payload['allowed_actions']['remove'])) {
            $this->render_review_form(
                'queue_review',
                'queue_item_id',
                $queue_item['queue_item_id'],
                true,
                true,
                ! empty($payload['allowed_actions']['approve'])
            );
        }
        if (empty($payload['allowed_actions']['approve']) && ! empty($payload['allowed_actions']['approve_block_reason'])) {
            echo '<p class="content-ops-muted">' . esc_html($payload['allowed_actions']['approve_block_reason']) . '</p>';
        }
        if (! empty($payload['allowed_actions']['schedule'])) {
            $this->render_schedule_form($queue_item['queue_item_id']);
        } elseif (! empty($payload['allowed_actions']['schedule_block_reason'])) {
            echo '<p class="content-ops-muted">' . esc_html($payload['allowed_actions']['schedule_block_reason']) . '</p>';
        }
        $this->render_history_list($payload['review_history']);
        echo '</aside></div>';
        $this->render_fast_lane_card($payload['fast_lane']);
    }

    private function render_priority_review_list($title, $rows, $target_type) {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html($title) . '</h2>';
        if (empty($rows)) {
            echo '<p class="content-ops-muted">' . esc_html__('No urgent items are queued right now.', 'content-ops-approval-ui') . '</p>';
            echo '</div>';
            return;
        }

        echo '<ul class="content-ops-priority-list">';
        foreach ($rows as $row) {
            $detail_url = $this->build_priority_link($target_type, isset($row['detail_target_id']) ? $row['detail_target_id'] : '');
            echo '<li class="content-ops-priority-item">';
            if ($detail_url) {
                echo '<a class="content-ops-priority-link" href="' . esc_url($detail_url) . '">' . esc_html((string) $row['title']) . '</a>';
            } else {
                echo '<span class="content-ops-priority-link">' . esc_html((string) $row['title']) . '</span>';
            }
            if (! empty($row['subtitle'])) {
                echo '<div class="content-ops-muted">' . esc_html((string) $row['subtitle']) . '</div>';
            }
            echo '<div class="content-ops-priority-meta">';
            if ('draft' === $target_type) {
                echo '<span class="content-ops-pill">' . esc_html((string) $row['operator_signal']) . '</span> ';
                echo '<span class="content-ops-pill">' . esc_html((string) $row['approval_state']) . '</span>';
            } elseif ('social_package' === $target_type) {
                echo '<span class="content-ops-pill">' . esc_html((string) $row['linkage_state']) . '</span> ';
                echo '<span class="content-ops-pill">' . esc_html((string) $row['approval_state']) . '</span>';
            } elseif ('media_asset' === $target_type) {
                echo '<span class="content-ops-pill">' . esc_html((string) $row['approval_state']) . '</span> ';
                echo '<span class="content-ops-pill">' . esc_html(! empty($row['asset_complete']) ? __('Ready', 'content-ops-approval-ui') : __('Blocked', 'content-ops-approval-ui')) . '</span>';
            } else {
                echo '<span class="content-ops-pill">' . esc_html((string) $row['queue_state']) . '</span> ';
                echo '<span class="content-ops-pill">' . esc_html((string) $row['queue_review_state']) . '</span>';
            }
            echo '</div>';
            echo '</li>';
        }
        echo '</ul>';
        echo '</div>';
    }

    private function render_draft_filter_bar($filters) {
        echo '<form class="content-ops-filter-bar" method="get">';
        echo '<input type="hidden" name="page" value="content-ops-approval-drafts">';
        echo '<input type="search" name="search" value="' . esc_attr(isset($filters['search']) ? $filters['search'] : '') . '" placeholder="' . esc_attr__('Search drafts', 'content-ops-approval-ui') . '">';
        $this->render_select_input(
            'approval_state',
            isset($filters['approval_state']) ? $filters['approval_state'] : '',
            array(
                '' => __('All approval states', 'content-ops-approval-ui'),
                'pending_review' => __('Pending review', 'content-ops-approval-ui'),
                'needs_edits' => __('Needs edits', 'content-ops-approval-ui'),
                'approved' => __('Approved', 'content-ops-approval-ui'),
                'rejected' => __('Rejected', 'content-ops-approval-ui'),
            )
        );
        $this->render_select_input(
            'operator_signal',
            isset($filters['operator_signal']) ? $filters['operator_signal'] : '',
            array(
                '' => __('All operator signals', 'content-ops-approval-ui'),
                'ready_for_review' => __('Ready for review', 'content-ops-approval-ui'),
                'review_flag_pending' => __('Review flag pending', 'content-ops-approval-ui'),
                'needs_revision' => __('Needs revision', 'content-ops-approval-ui'),
                'blocked_quality' => __('Blocked quality', 'content-ops-approval-ui'),
                'approved_ready_for_phase_3' => __('Approved ready forward', 'content-ops-approval-ui'),
                'approved_with_review_flags' => __('Approved with flags', 'content-ops-approval-ui'),
            )
        );
        echo '<input type="text" name="source_domain" value="' . esc_attr(isset($filters['source_domain']) ? $filters['source_domain'] : '') . '" placeholder="' . esc_attr__('Source domain', 'content-ops-approval-ui') . '">';
        echo '<input type="text" name="template_id" value="' . esc_attr(isset($filters['template_id']) ? $filters['template_id'] : '') . '" placeholder="' . esc_attr__('Template ID', 'content-ops-approval-ui') . '">';
        echo '<input type="text" name="category" value="' . esc_attr(isset($filters['category']) ? $filters['category'] : '') . '" placeholder="' . esc_attr__('Category', 'content-ops-approval-ui') . '">';
        echo '<button class="button button-secondary" type="submit">' . esc_html__('Filter', 'content-ops-approval-ui') . '</button>';
        echo '<a class="button" href="' . esc_url($this->build_admin_page_url('content-ops-approval-drafts')) . '">' . esc_html__('Clear', 'content-ops-approval-ui') . '</a>';
        echo '</form>';
    }

    private function render_social_filter_bar($filters) {
        echo '<form class="content-ops-filter-bar" method="get">';
        echo '<input type="hidden" name="page" value="content-ops-approval-social">';
        echo '<input type="search" name="search" value="' . esc_attr(isset($filters['search']) ? $filters['search'] : '') . '" placeholder="' . esc_attr__('Search social packages', 'content-ops-approval-ui') . '">';
        $this->render_select_input(
            'approval_state',
            isset($filters['approval_state']) ? $filters['approval_state'] : '',
            array(
                '' => __('All approval states', 'content-ops-approval-ui'),
                'pending_review' => __('Pending review', 'content-ops-approval-ui'),
                'needs_edits' => __('Needs edits', 'content-ops-approval-ui'),
                'approved' => __('Approved', 'content-ops-approval-ui'),
                'rejected' => __('Rejected', 'content-ops-approval-ui'),
            )
        );
        $this->render_select_input(
            'linkage_state',
            isset($filters['linkage_state']) ? $filters['linkage_state'] : '',
            array(
                '' => __('All linkage states', 'content-ops-approval-ui'),
                'unlinked' => __('Unlinked', 'content-ops-approval-ui'),
                'packaging_pending_review' => __('Packaging pending review', 'content-ops-approval-ui'),
                'ready_for_social_review' => __('Ready for social review', 'content-ops-approval-ui'),
                'approved_for_queue' => __('Approved for queue', 'content-ops-approval-ui'),
                'facebook_publish_failed' => __('Facebook publish failed', 'content-ops-approval-ui'),
            )
        );
        echo '<button class="button button-secondary" type="submit">' . esc_html__('Filter', 'content-ops-approval-ui') . '</button>';
        echo '<a class="button" href="' . esc_url($this->build_admin_page_url('content-ops-approval-social')) . '">' . esc_html__('Clear', 'content-ops-approval-ui') . '</a>';
        echo '</form>';
    }

    private function render_media_filter_bar($filters) {
        echo '<form class="content-ops-filter-bar" method="get">';
        echo '<input type="hidden" name="page" value="content-ops-approval-media">';
        echo '<input type="search" name="search" value="' . esc_attr(isset($filters['search']) ? $filters['search'] : '') . '" placeholder="' . esc_attr__('Search media assets', 'content-ops-approval-ui') . '">';
        $this->render_select_input(
            'approval_state',
            isset($filters['approval_state']) ? $filters['approval_state'] : '',
            array(
                '' => __('All approval states', 'content-ops-approval-ui'),
                'pending_review' => __('Pending review', 'content-ops-approval-ui'),
                'needs_edits' => __('Needs edits', 'content-ops-approval-ui'),
                'approved' => __('Approved', 'content-ops-approval-ui'),
                'rejected' => __('Rejected', 'content-ops-approval-ui'),
            )
        );
        $this->render_select_input(
            'asset_source_kind',
            isset($filters['asset_source_kind']) ? $filters['asset_source_kind'] : '',
            array(
                '' => __('All source kinds', 'content-ops-approval-ui'),
                'owned' => __('Owned', 'content-ops-approval-ui'),
                'licensed' => __('Licensed', 'content-ops-approval-ui'),
                'ai_generated' => __('AI generated', 'content-ops-approval-ui'),
            )
        );
        echo '<button class="button button-secondary" type="submit">' . esc_html__('Filter', 'content-ops-approval-ui') . '</button>';
        echo '<a class="button" href="' . esc_url($this->build_admin_page_url('content-ops-approval-media')) . '">' . esc_html__('Clear', 'content-ops-approval-ui') . '</a>';
        echo '</form>';
    }

    private function render_queue_filter_bar($filters) {
        echo '<form class="content-ops-filter-bar" method="get">';
        echo '<input type="hidden" name="page" value="content-ops-approval-queue">';
        $this->render_select_input(
            'queue_type',
            isset($filters['queue_type']) ? $filters['queue_type'] : '',
            array(
                '' => __('All queue types', 'content-ops-approval-ui'),
                'blog_publish' => __('Blog publish', 'content-ops-approval-ui'),
                'facebook_publish' => __('Facebook publish', 'content-ops-approval-ui'),
            )
        );
        echo '<input type="text" name="queue_state" value="' . esc_attr(isset($filters['queue_state']) ? $filters['queue_state'] : '') . '" placeholder="' . esc_attr__('Queue state', 'content-ops-approval-ui') . '">';
        $this->render_select_input(
            'queue_review_state',
            isset($filters['queue_review_state']) ? $filters['queue_review_state'] : '',
            array(
                '' => __('All review states', 'content-ops-approval-ui'),
                'pending_review' => __('Pending review', 'content-ops-approval-ui'),
                'approved' => __('Approved', 'content-ops-approval-ui'),
                'needs_edits' => __('Needs edits', 'content-ops-approval-ui'),
                'removed' => __('Removed', 'content-ops-approval-ui'),
            )
        );
        $this->render_select_input(
            'schedule_allowed',
            isset($filters['schedule_allowed']) ? $filters['schedule_allowed'] : '',
            array(
                '' => __('Any schedule state', 'content-ops-approval-ui'),
                'true' => __('Schedule allowed', 'content-ops-approval-ui'),
                'false' => __('Schedule blocked', 'content-ops-approval-ui'),
            )
        );
        echo '<label class="content-ops-checkbox"><input type="checkbox" name="blocked_only" value="true" ' . checked(isset($filters['blocked_only']) ? $filters['blocked_only'] : '', 'true', false) . '> ' . esc_html__('Blocked only', 'content-ops-approval-ui') . '</label>';
        echo '<button class="button button-secondary" type="submit">' . esc_html__('Filter', 'content-ops-approval-ui') . '</button>';
        echo '<a class="button" href="' . esc_url($this->build_admin_page_url('content-ops-approval-queue')) . '">' . esc_html__('Clear', 'content-ops-approval-ui') . '</a>';
        echo '</form>';
    }

    private function render_draft_detail_review_form($draft) {
        echo '<form class="content-ops-review-form" method="post">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="draft_review">';
        echo '<input type="hidden" name="draft_id" value="' . esc_attr($draft['draft_id']) . '">';
        echo '<input type="hidden" name="current_headline_selected" value="' . esc_attr((string) $draft['headline_selected']) . '">';
        if (! empty($draft['headline_variants']) && is_array($draft['headline_variants'])) {
            echo '<h3>' . esc_html__('Headline Variant', 'content-ops-approval-ui') . '</h3>';
            echo '<div class="content-ops-option-list">';
            foreach ($draft['headline_variants'] as $index => $variant) {
                $field_id = 'content_ops_draft_variant_' . absint($index);
                echo '<label class="content-ops-option-card" for="' . esc_attr($field_id) . '">';
                echo '<input type="radio" id="' . esc_attr($field_id) . '" name="selected_headline_variant" value="' . esc_attr((string) $variant) . '" ' . checked((string) $draft['headline_selected'], (string) $variant, false) . '>';
                echo '<span>' . esc_html((string) $variant) . '</span>';
                echo '</label>';
            }
            echo '</div>';
        } else {
            echo '<input type="hidden" name="selected_headline_variant" value="' . esc_attr((string) $draft['headline_selected']) . '">';
        }
        echo '<p><label for="content_ops_draft_review_note">' . esc_html__('Review Note', 'content-ops-approval-ui') . '</label></p>';
        echo '<p><textarea rows="4" name="review_note" id="content_ops_draft_review_note"></textarea></p>';
        echo '<p class="content-ops-inline-actions">';
        echo '<button class="button button-primary" type="submit" name="review_outcome" value="approved">' . esc_html__('Approve Draft', 'content-ops-approval-ui') . '</button>';
        echo '<button class="button" type="submit" name="review_outcome" value="needs_edits">' . esc_html__('Needs Edits', 'content-ops-approval-ui') . '</button>';
        echo '<button class="button button-secondary" type="submit" name="review_outcome" value="rejected">' . esc_html__('Reject', 'content-ops-approval-ui') . '</button>';
        echo '</p></form>';
    }

    private function render_social_detail_review_form($package) {
        echo '<form class="content-ops-review-form" method="post">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="social_review">';
        echo '<input type="hidden" name="social_package_id" value="' . esc_attr($package['social_package_id']) . '">';
        echo '<input type="hidden" name="current_variant_label" value="' . esc_attr((string) $package['selected_variant_label']) . '">';
        if (! empty($package['variant_options']) && is_array($package['variant_options'])) {
            echo '<h3>' . esc_html__('Prepared Variant', 'content-ops-approval-ui') . '</h3>';
            echo '<div class="content-ops-option-list">';
            foreach ($package['variant_options'] as $index => $variant) {
                $field_id = 'content_ops_social_variant_' . absint($index);
                $label = isset($variant['label']) ? (string) $variant['label'] : '';
                echo '<label class="content-ops-option-card" for="' . esc_attr($field_id) . '">';
                echo '<input type="radio" id="' . esc_attr($field_id) . '" name="selected_variant_label" value="' . esc_attr($label) . '" ' . checked((string) $package['selected_variant_label'], $label, false) . '>';
                echo '<strong>' . esc_html($label) . '</strong>';
                echo '<span><strong>' . esc_html__('Hook', 'content-ops-approval-ui') . ':</strong> ' . esc_html(isset($variant['hook_text']) ? (string) $variant['hook_text'] : '') . '</span>';
                echo '<span><strong>' . esc_html__('Caption', 'content-ops-approval-ui') . ':</strong> ' . esc_html(isset($variant['caption_text']) ? (string) $variant['caption_text'] : '') . '</span>';
                echo '<span><strong>' . esc_html__('CTA', 'content-ops-approval-ui') . ':</strong> ' . esc_html(isset($variant['comment_cta_text']) ? (string) $variant['comment_cta_text'] : '') . '</span>';
                echo '</label>';
            }
            echo '</div>';
        } else {
            echo '<input type="hidden" name="selected_variant_label" value="' . esc_attr((string) $package['selected_variant_label']) . '">';
        }
        echo '<p><label for="content_ops_social_review_note">' . esc_html__('Review Note', 'content-ops-approval-ui') . '</label></p>';
        echo '<p><textarea rows="4" name="review_note" id="content_ops_social_review_note"></textarea></p>';
        echo '<p class="content-ops-inline-actions">';
        echo '<button class="button button-primary" type="submit" name="review_outcome" value="approved">' . esc_html__('Approve Package', 'content-ops-approval-ui') . '</button>';
        echo '<button class="button" type="submit" name="review_outcome" value="needs_edits">' . esc_html__('Needs Edits', 'content-ops-approval-ui') . '</button>';
        echo '<button class="button button-secondary" type="submit" name="review_outcome" value="rejected">' . esc_html__('Reject', 'content-ops-approval-ui') . '</button>';
        echo '</p></form>';
    }

    private function render_inline_note_review_form($action, $id_key, $id_value, $outcome, $button_label) {
        $field_id = 'content_ops_note_' . md5($action . '|' . $id_value . '|' . $outcome);
        echo '<form class="content-ops-inline-note-form" method="post">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="' . esc_attr($id_key) . '" value="' . esc_attr($id_value) . '">';
        echo '<input type="hidden" name="review_outcome" value="' . esc_attr($outcome) . '">';
        echo '<label class="screen-reader-text" for="' . esc_attr($field_id) . '">' . esc_html__('Action note', 'content-ops-approval-ui') . '</label>';
        echo '<input class="regular-text" type="text" name="review_note" id="' . esc_attr($field_id) . '" placeholder="' . esc_attr__('Short actionable note', 'content-ops-approval-ui') . '">';
        echo '<button class="button" type="submit">' . esc_html($button_label) . '</button>';
        echo '</form>';
    }

    private function render_select_input($name, $selected_value, $options) {
        echo '<select name="' . esc_attr($name) . '">';
        foreach ($options as $value => $label) {
            echo '<option value="' . esc_attr((string) $value) . '" ' . selected((string) $selected_value, (string) $value, false) . '>' . esc_html((string) $label) . '</option>';
        }
        echo '</select>';
    }

    private function build_api_path($path, $filters = array()) {
        $query = array();
        foreach ((array) $filters as $key => $value) {
            if (null === $value || '' === $value) {
                continue;
            }
            $query[$key] = $value;
        }

        if (empty($query)) {
            return $path;
        }

        return $path . '?' . http_build_query($query, '', '&', PHP_QUERY_RFC3986);
    }

    private function build_admin_page_url($page, $extra_args = array(), $filter_keys = array()) {
        $args = array('page' => $page);
        foreach ((array) $filter_keys as $filter_key) {
            if (! isset($_GET[$filter_key])) {
                continue;
            }
            $value = sanitize_text_field(wp_unslash($_GET[$filter_key]));
            if ('' === $value) {
                continue;
            }
            $args[$filter_key] = $value;
        }
        foreach ((array) $extra_args as $key => $value) {
            if (null === $value || '' === $value) {
                continue;
            }
            $args[$key] = $value;
        }
        return add_query_arg($args, admin_url('admin.php'));
    }

    private function build_priority_link($target_type, $detail_target_id) {
        if (! $detail_target_id) {
            return '';
        }
        if ('draft' === $target_type) {
            return $this->build_admin_page_url('content-ops-approval-drafts', array('draft_id' => $detail_target_id));
        }
        if ('social_package' === $target_type) {
            return $this->build_admin_page_url('content-ops-approval-social', array('social_package_id' => $detail_target_id));
        }
        if ('media_asset' === $target_type) {
            return $this->build_admin_page_url('content-ops-approval-media', array('asset_record_id' => $detail_target_id));
        }
        if ('queue_item' === $target_type) {
            return $this->build_admin_page_url('content-ops-approval-queue', array('queue_item_id' => $detail_target_id));
        }
        return '';
    }

    private function get_draft_filter_keys() {
        return array('search', 'approval_state', 'operator_signal', 'source_domain', 'template_id', 'category');
    }

    private function get_social_filter_keys() {
        return array('search', 'approval_state', 'linkage_state');
    }

    private function get_media_filter_keys() {
        return array('search', 'approval_state', 'asset_source_kind');
    }

    private function get_queue_filter_keys() {
        return array('queue_type', 'queue_state', 'queue_review_state', 'blocked_only', 'schedule_allowed');
    }

    private function get_draft_filters_from_request() {
        return array(
            'search' => isset($_GET['search']) ? sanitize_text_field(wp_unslash($_GET['search'])) : '',
            'approval_state' => isset($_GET['approval_state']) ? sanitize_text_field(wp_unslash($_GET['approval_state'])) : '',
            'operator_signal' => isset($_GET['operator_signal']) ? sanitize_text_field(wp_unslash($_GET['operator_signal'])) : '',
            'source_domain' => isset($_GET['source_domain']) ? sanitize_text_field(wp_unslash($_GET['source_domain'])) : '',
            'template_id' => isset($_GET['template_id']) ? sanitize_text_field(wp_unslash($_GET['template_id'])) : '',
            'category' => isset($_GET['category']) ? sanitize_text_field(wp_unslash($_GET['category'])) : '',
        );
    }

    private function get_social_filters_from_request() {
        return array(
            'search' => isset($_GET['search']) ? sanitize_text_field(wp_unslash($_GET['search'])) : '',
            'approval_state' => isset($_GET['approval_state']) ? sanitize_text_field(wp_unslash($_GET['approval_state'])) : '',
            'linkage_state' => isset($_GET['linkage_state']) ? sanitize_text_field(wp_unslash($_GET['linkage_state'])) : '',
        );
    }

    private function get_media_filters_from_request() {
        return array(
            'search' => isset($_GET['search']) ? sanitize_text_field(wp_unslash($_GET['search'])) : '',
            'approval_state' => isset($_GET['approval_state']) ? sanitize_text_field(wp_unslash($_GET['approval_state'])) : '',
            'asset_source_kind' => isset($_GET['asset_source_kind']) ? sanitize_text_field(wp_unslash($_GET['asset_source_kind'])) : '',
        );
    }

    private function get_queue_filters_from_request() {
        return array(
            'queue_type' => isset($_GET['queue_type']) ? sanitize_text_field(wp_unslash($_GET['queue_type'])) : '',
            'queue_state' => isset($_GET['queue_state']) ? sanitize_text_field(wp_unslash($_GET['queue_state'])) : '',
            'queue_review_state' => isset($_GET['queue_review_state']) ? sanitize_text_field(wp_unslash($_GET['queue_review_state'])) : '',
            'blocked_only' => isset($_GET['blocked_only']) ? sanitize_text_field(wp_unslash($_GET['blocked_only'])) : '',
            'schedule_allowed' => isset($_GET['schedule_allowed']) ? sanitize_text_field(wp_unslash($_GET['schedule_allowed'])) : '',
        );
    }

    private function has_actionable_note($note) {
        $normalized = trim(wp_strip_all_tags((string) $note));
        if (strlen($normalized) < 8) {
            return false;
        }
        return str_word_count($normalized) >= 2;
    }

    private function render_metric_card($title, $metrics) {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html($title) . '</h2>';
        foreach ($metrics as $label => $value) {
            echo '<p><span class="content-ops-pill">' . esc_html((string) $label) . '</span> ';
            echo '<span class="content-ops-metric">' . esc_html((string) $value) . '</span></p>';
        }
        echo '</div>';
    }

    private function render_validation_local_checks($payload) {
        $settings = $this->get_settings();
        $api_base_url = $this->get_api_base_url();
        $shared_secret = $this->get_shared_secret();
        $api_topology = $this->analyze_api_base_url($api_base_url);
        $user = wp_get_current_user();
        echo '<div class="content-ops-dashboard-grid">';
        $this->render_metric_card(__('Local Validation Checks', 'content-ops-approval-ui'), array(
            __('Current user', 'content-ops-approval-ui') => ($user instanceof WP_User && $user->exists()) ? $user->user_login : __('Unknown', 'content-ops-approval-ui'),
            __('Review capability', 'content-ops-approval-ui') => current_user_can(self::REVIEW_CAPABILITY) ? __('Yes', 'content-ops-approval-ui') : __('No', 'content-ops-approval-ui'),
            __('API base URL set', 'content-ops-approval-ui') => $api_base_url ? __('Yes', 'content-ops-approval-ui') : __('No', 'content-ops-approval-ui'),
            __('Shared secret set', 'content-ops-approval-ui') => $shared_secret ? __('Yes', 'content-ops-approval-ui') : __('No', 'content-ops-approval-ui'),
            __('API reachability mode', 'content-ops-approval-ui') => $api_topology['label'],
            __('Settings source', 'content-ops-approval-ui') => (
                defined('CONTENT_OPS_APPROVAL_UI_API_BASE_URL') || defined('CONTENT_OPS_APPROVAL_UI_SHARED_SECRET')
            ) ? __('Locked constant', 'content-ops-approval-ui') : __('Plugin settings', 'content-ops-approval-ui'),
        ));
        if (is_array($payload)) {
            $this->render_metric_card(__('Backend Validation Snapshot', 'content-ops-approval-ui'), array(
                __('Validation status', 'content-ops-approval-ui') => isset($payload['status']) ? $payload['status'] : '',
                __('Draft rows visible', 'content-ops-approval-ui') => isset($payload['record_counts']['draft_rows']) ? $payload['record_counts']['draft_rows'] : 0,
                __('Social rows visible', 'content-ops-approval-ui') => isset($payload['record_counts']['social_package_rows']) ? $payload['record_counts']['social_package_rows'] : 0,
                __('Media rows visible', 'content-ops-approval-ui') => isset($payload['record_counts']['media_asset_rows']) ? $payload['record_counts']['media_asset_rows'] : 0,
                __('Queue rows visible', 'content-ops-approval-ui') => isset($payload['record_counts']['queue_rows']) ? $payload['record_counts']['queue_rows'] : 0,
                __('Activation signal', 'content-ops-approval-ui') => isset($payload['workflow_snapshot']['activation_signal']) ? $payload['workflow_snapshot']['activation_signal'] : '',
            ));
        } else {
            $this->render_metric_card(__('Backend Validation Snapshot', 'content-ops-approval-ui'), array(
                __('Validation status', 'content-ops-approval-ui') => __('Unavailable', 'content-ops-approval-ui'),
                __('Draft rows visible', 'content-ops-approval-ui') => __('Unknown', 'content-ops-approval-ui'),
                __('Social rows visible', 'content-ops-approval-ui') => __('Unknown', 'content-ops-approval-ui'),
                __('Media rows visible', 'content-ops-approval-ui') => __('Unknown', 'content-ops-approval-ui'),
                __('Queue rows visible', 'content-ops-approval-ui') => __('Unknown', 'content-ops-approval-ui'),
                __('Activation signal', 'content-ops-approval-ui') => __('Unknown', 'content-ops-approval-ui'),
            ));
        }
        echo '</div>';
        $this->render_api_reachability_guidance($api_base_url);
    }

    private function render_validation_backend_checks($payload) {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html__('Backend Endpoint Checks', 'content-ops-approval-ui') . '</h2>';
        if (empty($payload['endpoint_checks']) || ! is_array($payload['endpoint_checks'])) {
            echo '<p class="content-ops-muted">' . esc_html__('No backend endpoint checks were returned.', 'content-ops-approval-ui') . '</p>';
            echo '</div>';
            return;
        }
        echo '<table class="widefat striped"><thead><tr>';
        echo '<th>' . esc_html__('Check', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Path', 'content-ops-approval-ui') . '</th>';
        echo '<th>' . esc_html__('Result', 'content-ops-approval-ui') . '</th>';
        echo '</tr></thead><tbody>';
        foreach ($payload['endpoint_checks'] as $label => $row) {
            echo '<tr>';
            echo '<td>' . esc_html((string) $label) . '</td>';
            echo '<td><code>' . esc_html(isset($row['path']) ? (string) $row['path'] : '') . '</code></td>';
            echo '<td>' . $this->render_status_badge(! empty($row['ok']), ! empty($row['ok']) ? __('OK', 'content-ops-approval-ui') : __('Failed', 'content-ops-approval-ui')) . '</td>';
            echo '</tr>';
        }
        echo '</tbody></table>';
        if (! empty($payload['notes']) && is_array($payload['notes'])) {
            echo '<h3>' . esc_html__('Validation Notes', 'content-ops-approval-ui') . '</h3>';
            echo '<ul class="content-ops-history-list">';
            foreach ($payload['notes'] as $note) {
                echo '<li>' . esc_html((string) $note) . '</li>';
            }
            echo '</ul>';
        }
        echo '</div>';
    }

    private function render_validation_manual_checklist() {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html__('Live Admin Validation Checklist', 'content-ops-approval-ui') . '</h2>';
        echo '<ol class="content-ops-validation-list">';
        echo '<li>' . esc_html__('Confirm the Operator API base URL is appropriate for your topology. Localhost is only valid when WordPress and the operator API run on the same machine.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open Dashboard and confirm counts, recent activity links, and alert links load without backend errors.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open one draft detail, approve it or mark it needs edits, and confirm the success notice appears.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open one social-package detail, submit a review action, and confirm the queue state refreshes.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open one media-asset detail, submit a review action, and confirm linked asset readiness updates safely.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open one queue detail, verify blocked approve reasons show when applicable, and verify eligible queue items can still be approved.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Open one queue item that is schedule-eligible and confirm the blog schedule form submits successfully.', 'content-ops-approval-ui') . '</li>';
        echo '<li>' . esc_html__('Temporarily break the API URL or secret and confirm the plugin shows a safe admin error instead of a blank page.', 'content-ops-approval-ui') . '</li>';
        echo '</ol>';
        echo '</div>';
    }

    private function render_activity_list($title, $rows) {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html($title) . '</h2>';
        if (empty($rows)) {
            echo '<p class="content-ops-muted">' . esc_html__('No recent review activity recorded yet.', 'content-ops-approval-ui') . '</p>';
            echo '</div>';
            return;
        }
        echo '<ul class="content-ops-history-list">';
        foreach ($rows as $row) {
            $summary = sprintf(
                '%s -> %s',
                isset($row['activity_type']) ? (string) $row['activity_type'] : '',
                isset($row['review_outcome']) ? (string) $row['review_outcome'] : ''
            );
            $detail_url = $this->build_activity_admin_link($row);
            echo '<li><strong>';
            if ($detail_url) {
                echo '<a href="' . esc_url($detail_url) . '">' . esc_html($summary) . '</a>';
            } else {
                echo esc_html($summary);
            }
            echo '</strong>';
            if (! empty($row['entity_id'])) {
                $entity_text = (string) $row['entity_id'];
                if ($detail_url) {
                    echo ' <span class="content-ops-muted"><a href="' . esc_url($detail_url) . '">' . esc_html($entity_text) . '</a></span>';
                } else {
                    echo ' <span class="content-ops-muted">' . esc_html($entity_text) . '</span>';
                }
            }
            if (! empty($row['occurred_at'])) {
                echo '<br>' . esc_html((string) $row['occurred_at']);
            }
            if (! empty($row['review_notes']) && is_array($row['review_notes'])) {
                echo '<br>' . esc_html(implode(' | ', array_map('strval', $row['review_notes'])));
            }
            echo '</li>';
        }
        echo '</ul>';
        echo '</div>';
    }

    private function render_alert_list($title, $rows) {
        echo '<div class="content-ops-card">';
        echo '<h2>' . esc_html($title) . '</h2>';
        if (empty($rows)) {
            echo '<p class="content-ops-muted">' . esc_html__('No current alerts.', 'content-ops-approval-ui') . '</p>';
            echo '</div>';
            return;
        }
        echo '<ul class="content-ops-history-list">';
        foreach ($rows as $row) {
            $severity = isset($row['severity']) ? (string) $row['severity'] : 'warning';
            $title_text = isset($row['title']) ? (string) $row['title'] : '';
            $message = isset($row['message']) ? (string) $row['message'] : '';
            $detail_url = $this->build_alert_admin_link($row);
            echo '<li><strong>' . esc_html($severity) . ':</strong> ';
            if ($detail_url) {
                echo '<a href="' . esc_url($detail_url) . '">' . esc_html($title_text) . '</a>';
            } else {
                echo esc_html($title_text);
            }
            if ($message) {
                echo '<br>' . esc_html($message);
            }
            if (! empty($row['occurred_at'])) {
                echo '<br><span class="content-ops-muted">' . esc_html((string) $row['occurred_at']) . '</span>';
            }
            echo '</li>';
        }
        echo '</ul>';
        echo '</div>';
    }

    private function render_meta_list($items) {
        echo '<ul class="content-ops-meta-list">';
        foreach ($items as $label => $value) {
            echo '<li><strong>' . esc_html($label) . ':</strong> ' . esc_html((string) $value) . '</li>';
        }
        echo '</ul>';
    }

    private function render_link_block($label, $url, $link_text) {
        echo '<p><strong>' . esc_html($label) . ':</strong> ';
        echo '<a href="' . esc_url($url) . '" target="_blank" rel="noopener noreferrer">' . esc_html($link_text) . '</a>';
        echo '</p>';
    }

    private function render_status_badge($ok, $label) {
        $class = $ok ? 'content-ops-status-ok' : 'content-ops-status-fail';
        return '<span class="content-ops-pill ' . esc_attr($class) . '">' . esc_html($label) . '</span>';
    }

    private function render_topology_badge($variant, $label) {
        $class = 'content-ops-status-warn';
        if ('ok' === $variant) {
            $class = 'content-ops-status-ok';
        } elseif ('fail' === $variant) {
            $class = 'content-ops-status-fail';
        }

        return '<span class="content-ops-pill ' . esc_attr($class) . '">' . esc_html($label) . '</span>';
    }

    private function render_api_reachability_guidance($api_base_url) {
        $analysis = $this->analyze_api_base_url($api_base_url);

        if ('remote_ready' === $analysis['mode']) {
            return;
        }

        echo '<div class="content-ops-card content-ops-guidance-card">';
        echo '<h2>' . esc_html__('Operator API Reachability Guidance', 'content-ops-approval-ui') . '</h2>';
        echo '<p>' . $this->render_topology_badge($analysis['variant'], $analysis['label']) . '</p>';
        echo '<p>' . esc_html($analysis['summary']) . '</p>';
        echo '<p class="content-ops-muted">' . esc_html($analysis['recommendation']) . '</p>';

        if (! empty($analysis['example_url'])) {
            echo '<p><strong>' . esc_html__('Recommended pattern:', 'content-ops-approval-ui') . '</strong> <code>' . esc_html($analysis['example_url']) . '</code></p>';
        }

        echo '</div>';
    }

    private function build_activity_admin_link($row) {
        if (! is_array($row) || empty($row['detail_target_type']) || empty($row['detail_target_id'])) {
            return '';
        }

        if ('draft' === $row['detail_target_type']) {
            return admin_url('admin.php?page=content-ops-approval-drafts&draft_id=' . rawurlencode((string) $row['detail_target_id']));
        }
        if ('social_package' === $row['detail_target_type']) {
            return admin_url('admin.php?page=content-ops-approval-social&social_package_id=' . rawurlencode((string) $row['detail_target_id']));
        }
        if ('media_asset' === $row['detail_target_type']) {
            return admin_url('admin.php?page=content-ops-approval-media&asset_record_id=' . rawurlencode((string) $row['detail_target_id']));
        }
        if ('queue_item' === $row['detail_target_type']) {
            return admin_url('admin.php?page=content-ops-approval-queue&queue_item_id=' . rawurlencode((string) $row['detail_target_id']));
        }

        return '';
    }

    private function build_alert_admin_link($row) {
        if (! is_array($row) || empty($row['queue_item_id'])) {
            return '';
        }

        return admin_url('admin.php?page=content-ops-approval-queue&queue_item_id=' . rawurlencode((string) $row['queue_item_id']));
    }

    private function render_history_list($history) {
        echo '<h3>' . esc_html__('Approval History', 'content-ops-approval-ui') . '</h3>';
        if (empty($history)) {
            echo '<p class="content-ops-muted">' . esc_html__('No review history recorded yet.', 'content-ops-approval-ui') . '</p>';
            return;
        }
        echo '<ul class="content-ops-history-list">';
        foreach ($history as $row) {
            echo '<li><strong>' . esc_html($row['review_outcome']) . '</strong> ';
            echo esc_html(isset($row['reviewed_at']) ? $row['reviewed_at'] : '');
            if (! empty($row['review_notes'])) {
                echo ': ' . esc_html(implode(' | ', $row['review_notes']));
            }
            echo '</li>';
        }
        echo '</ul>';
    }

    private function render_ai_assistance_log($title, $entries) {
        echo '<h3>' . esc_html($title) . '</h3>';
        if (empty($entries) || ! is_array($entries)) {
            echo '<p class="content-ops-muted">' . esc_html__('No AI assistance recorded.', 'content-ops-approval-ui') . '</p>';
            return;
        }
        echo '<ul class="content-ops-history-list content-ops-ai-log-list">';
        foreach ($entries as $entry) {
            if (! is_array($entry)) {
                continue;
            }
            $skill_name = isset($entry['skill_name']) ? (string) $entry['skill_name'] : '';
            $target_field = isset($entry['target_field']) ? (string) $entry['target_field'] : '';
            $model_label = isset($entry['model_label']) ? (string) $entry['model_label'] : '';
            $created_at = isset($entry['created_at']) ? (string) $entry['created_at'] : '';
            echo '<li>';
            echo '<strong>' . esc_html($skill_name) . '</strong>';
            if ($target_field) {
                echo '<br><span>' . esc_html__('Target:', 'content-ops-approval-ui') . ' ' . esc_html($target_field) . '</span>';
            }
            if ($model_label) {
                echo '<br><span>' . esc_html__('Model:', 'content-ops-approval-ui') . ' ' . esc_html($model_label) . '</span>';
            }
            if ($created_at) {
                echo '<br><span class="content-ops-muted">' . esc_html($created_at) . '</span>';
            }
            echo '</li>';
        }
        echo '</ul>';
    }

    private function render_review_form($action, $id_key, $id_value, $hold_only = false, $allow_remove = false, $allow_approve = true) {
        echo '<form class="content-ops-review-form" method="post">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="' . esc_attr($id_key) . '" value="' . esc_attr($id_value) . '">';
        echo '<p><label for="' . esc_attr($id_key . '_note') . '">' . esc_html__('Review Note', 'content-ops-approval-ui') . '</label></p>';
        echo '<p><textarea rows="4" name="review_note" id="' . esc_attr($id_key . '_note') . '"></textarea></p>';
        echo '<p class="content-ops-inline-actions">';
        if ($allow_approve) {
            echo '<button class="button button-primary" type="submit" name="review_outcome" value="approved">' . esc_html__('Approve', 'content-ops-approval-ui') . '</button>';
        }
        if ($hold_only) {
            echo '<button class="button button-secondary" type="submit" name="review_outcome" value="hold">' . esc_html__('Hold', 'content-ops-approval-ui') . '</button>';
            if ($allow_remove) {
                echo '<button class="button button-secondary" type="submit" name="review_outcome" value="removed">' . esc_html__('Remove', 'content-ops-approval-ui') . '</button>';
            }
        } else {
            echo '<button class="button" type="submit" name="review_outcome" value="needs_edits">' . esc_html__('Needs Edits', 'content-ops-approval-ui') . '</button>';
            echo '<button class="button button-secondary" type="submit" name="review_outcome" value="rejected">' . esc_html__('Reject', 'content-ops-approval-ui') . '</button>';
        }
        echo '</p></form>';
    }

    private function render_schedule_form($queue_item_id) {
        echo '<form class="content-ops-schedule-form" method="post">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="queue_schedule">';
        echo '<input type="hidden" name="queue_item_id" value="' . esc_attr($queue_item_id) . '">';
        echo '<p><label for="content_ops_schedule_time">' . esc_html__('Set Schedule', 'content-ops-approval-ui') . '</label></p>';
        echo '<p><input type="datetime-local" name="scheduled_for" id="content_ops_schedule_time"></p>';
        echo '<p><button class="button button-primary" type="submit">' . esc_html__('Set Schedule', 'content-ops-approval-ui') . '</button></p>';
        echo '</form>';
    }

    private function render_inline_review_form($action, $id_key, $id_value, $outcome, $note) {
        echo '<form method="post" style="display:inline-block;">';
        wp_nonce_field('content_ops_approval_action');
        echo '<input type="hidden" name="content_ops_action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="' . esc_attr($id_key) . '" value="' . esc_attr($id_value) . '">';
        echo '<input type="hidden" name="review_outcome" value="' . esc_attr($outcome) . '">';
        echo '<input type="hidden" name="review_note" value="' . esc_attr($note) . '">';
        echo '<button class="button button-primary" type="submit">' . esc_html__('Approve', 'content-ops-approval-ui') . '</button>';
        echo '</form>';
    }

    private function render_fast_lane_card($payload) {
        echo '<div class="content-ops-card content-ops-fast-lane">';
        echo '<h2>' . esc_html__('Fast Lane', 'content-ops-approval-ui') . '</h2>';
        echo '<p><span class="content-ops-pill">' . esc_html($payload['status']) . '</span></p>';
        echo '<p>' . esc_html($payload['message']) . '</p>';
        echo '<p class="content-ops-muted">' . esc_html__('Recommendation badge, confidence lane, and shadow-mode comparison are reserved for the later autoapproval phase.', 'content-ops-approval-ui') . '</p>';
        echo '</div>';
    }

    private function render_api_error($error) {
        echo '<div class="notice notice-error notice-inline"><p>' . esc_html($error->get_error_message()) . '</p></div>';
    }

    private function render_page_open($title) {
        echo '<div class="wrap content-ops-wrap">';
        echo '<h1>' . esc_html($title) . '</h1>';
    }

    private function render_page_close() {
        echo '</div>';
    }

    private function is_http_url($value) {
        $normalized = trim((string) $value);
        return 0 === strpos($normalized, 'http://') || 0 === strpos($normalized, 'https://');
    }

    private function api_request($method, $path, $body = null) {
        $base_url = $this->get_api_base_url();
        $shared_secret = $this->get_shared_secret();

        if (! $base_url || ! $shared_secret) {
            return new WP_Error(
                'content_ops_missing_api_config',
                __('Operator API base URL and shared secret must be configured first.', 'content-ops-approval-ui')
            );
        }

        $args = array(
            'method'  => strtoupper($method),
            'timeout' => 20,
            'headers' => array(
                'Accept'                      => 'application/json',
                'Content-Type'                => 'application/json',
                'X-Content-Ops-Shared-Secret' => $shared_secret,
            ),
        );

        if (null !== $body) {
            $args['body'] = wp_json_encode($body);
        }

        $response = wp_remote_request(untrailingslashit($base_url) . $path, $args);
        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $decoded = json_decode(wp_remote_retrieve_body($response), true);
        if ($status_code >= 400) {
            $message = is_array($decoded) && isset($decoded['detail']) ? $decoded['detail'] : __('Unknown operator API error.', 'content-ops-approval-ui');
            return new WP_Error('content_ops_api_error', sanitize_text_field((string) $message));
        }
        if (! is_array($decoded)) {
            return new WP_Error('content_ops_api_error', __('Operator API returned invalid JSON.', 'content-ops-approval-ui'));
        }

        return $decoded;
    }

    private function get_settings() {
        $defaults = array(
            'api_base_url' => '',
            'shared_secret' => '',
        );

        return wp_parse_args(get_option(self::OPTION_KEY, array()), $defaults);
    }

    private function get_api_base_url() {
        if (defined('CONTENT_OPS_APPROVAL_UI_API_BASE_URL') && CONTENT_OPS_APPROVAL_UI_API_BASE_URL) {
            return CONTENT_OPS_APPROVAL_UI_API_BASE_URL;
        }
        $settings = $this->get_settings();
        return $settings['api_base_url'];
    }

    private function analyze_api_base_url($api_base_url) {
        if (! $api_base_url) {
            return array(
                'mode' => 'missing',
                'variant' => 'fail',
                'label' => __('Missing', 'content-ops-approval-ui'),
                'summary' => __('The operator API base URL is not configured yet.', 'content-ops-approval-ui'),
                'recommendation' => __('Set the base URL before trying to validate the approval UI. Use localhost only for same-machine testing, or a reachable HTTPS hostname for hosted WordPress.', 'content-ops-approval-ui'),
                'example_url' => 'https://ops-api.example.com',
            );
        }

        $parts = wp_parse_url($api_base_url);
        $scheme = isset($parts['scheme']) ? strtolower((string) $parts['scheme']) : '';
        $host = isset($parts['host']) ? strtolower((string) $parts['host']) : '';

        if (! $host) {
            return array(
                'mode' => 'invalid',
                'variant' => 'fail',
                'label' => __('Invalid URL', 'content-ops-approval-ui'),
                'summary' => __('The operator API base URL could not be parsed into a usable host.', 'content-ops-approval-ui'),
                'recommendation' => __('Use a full URL such as http://127.0.0.1:8765 for local same-machine testing or a reachable HTTPS hostname for hosted WordPress.', 'content-ops-approval-ui'),
                'example_url' => 'https://ops-api.example.com',
            );
        }

        if ($this->is_localhost_host($host)) {
            return array(
                'mode' => 'local_only',
                'variant' => 'warn',
                'label' => __('Localhost only', 'content-ops-approval-ui'),
                'summary' => __('This base URL only works when WordPress and the operator API run on the same machine.', 'content-ops-approval-ui'),
                'recommendation' => __('If WordPress is hosted elsewhere, replace localhost with a reachable HTTPS operator-API hostname and keep the shared secret enabled.', 'content-ops-approval-ui'),
                'example_url' => 'https://ops-api.example.com',
            );
        }

        if ($this->is_private_or_internal_host($host)) {
            return array(
                'mode' => 'internal_network',
                'variant' => 'warn',
                'label' => __('Internal network only', 'content-ops-approval-ui'),
                'summary' => __('This base URL points to a private or internal-only host.', 'content-ops-approval-ui'),
                'recommendation' => __('This can work only if the WordPress host can reach that internal network. Otherwise expose the operator API through a restricted HTTPS hostname.', 'content-ops-approval-ui'),
                'example_url' => 'https://ops-api.example.com',
            );
        }

        if ('https' !== $scheme) {
            return array(
                'mode' => 'remote_insecure',
                'variant' => 'warn',
                'label' => __('Remote over HTTP', 'content-ops-approval-ui'),
                'summary' => __('This URL is remotely reachable in shape, but it is not using HTTPS.', 'content-ops-approval-ui'),
                'recommendation' => __('For production or hosted WordPress, put the operator API behind HTTPS and keep the shared secret enabled.', 'content-ops-approval-ui'),
                'example_url' => 'https://ops-api.example.com',
            );
        }

        return array(
            'mode' => 'remote_ready',
            'variant' => 'ok',
            'label' => __('Remote-ready HTTPS', 'content-ops-approval-ui'),
            'summary' => __('This base URL looks appropriate for a separately hosted WordPress site.', 'content-ops-approval-ui'),
            'recommendation' => __('Keep the shared secret enabled and confirm the operator API host is restricted to the intended approval path.', 'content-ops-approval-ui'),
            'example_url' => '',
        );
    }

    private function is_localhost_host($host) {
        return in_array($host, array('127.0.0.1', 'localhost', '::1'), true);
    }

    private function is_private_or_internal_host($host) {
        if ($this->is_localhost_host($host)) {
            return false;
        }

        if (filter_var($host, FILTER_VALIDATE_IP)) {
            if (false !== filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                return false;
            }

            return true;
        }

        return (bool) preg_match('/(\.local|\.internal|\.lan|\.home|\.test)$/', $host);
    }

    private function get_shared_secret() {
        if (defined('CONTENT_OPS_APPROVAL_UI_SHARED_SECRET') && CONTENT_OPS_APPROVAL_UI_SHARED_SECRET) {
            return CONTENT_OPS_APPROVAL_UI_SHARED_SECRET;
        }
        $settings = $this->get_settings();
        return $settings['shared_secret'];
    }

    private function get_operator_label() {
        $user = wp_get_current_user();
        if ($user instanceof WP_User && $user->exists()) {
            return $user->user_login;
        }

        return 'wordpress_operator';
    }

    private function store_result_notice($response, $success_message) {
        if (is_wp_error($response)) {
            $message = $response->get_error_message();
            $type = 'error';
        } else {
            $message = $success_message;
            $type = 'success';
        }

        set_transient(
            self::NOTICE_TRANSIENT_PREFIX . get_current_user_id(),
            array(
                'message' => $message,
                'type' => $type,
            ),
            30
        );
    }

    private function render_notice() {
        $transient_key = self::NOTICE_TRANSIENT_PREFIX . get_current_user_id();
        $notice = get_transient($transient_key);
        if (! is_array($notice)) {
            return;
        }
        delete_transient($transient_key);
        $class = 'success' === $notice['type'] ? 'notice notice-success notice-inline' : 'notice notice-error notice-inline';
        echo '<div class="' . esc_attr($class) . '"><p>' . esc_html($notice['message']) . '</p></div>';
    }

    private function redirect_back() {
        $referer = wp_get_referer();
        if (! $referer) {
            $referer = admin_url('admin.php?page=content-ops-approval-dashboard');
        }
        wp_safe_redirect($referer);
        exit;
    }
}
