<?php
// Mock WordPress Environment for Local Standalone Testing
if (!class_exists('WP_Error')) {
    class WP_Error {
        public $code;
        public $message;
        public function __construct($code, $message) {
            $this->code = $code;
            $this->message = $message;
        }
    }
}

function is_wp_error($thing) {
    return $thing instanceof WP_Error;
}

function wp_json_encode($data) {
    return json_encode($data);
}

function sanitize_text_field($text) {
    return strip_tags($text);
}

function sanitize_textarea_field($text) {
    return strip_tags($text);
}

function __($text, $domain) {
    return $text;
}

// Global state simulation for options
$options_db = [
    'nexuspress_license_key' => 'nexus_lic_9923847294823'
];

function get_option($key, $default = '') {
    global $options_db;
    return isset($options_db[$key]) ? $options_db[$key] : $default;
}

// Mocking WP HTTP posting using PHP's native file_get_contents
function wp_remote_post($url, $args) {
    $header_strings = [];
    foreach ($args['headers'] as $name => $val) {
        $header_strings[] = "$name: $val";
    }

    $options = [
        'http' => [
            'method'  => 'POST',
            'header'  => implode("\r\n", $header_strings),
            'content' => $args['body'],
            'timeout' => $args['timeout'],
            'ignore_errors' => true // allows retrieving non-200 responses
        ]
    ];

    $context = stream_context_create($options);
    $response_body = @file_get_contents($url, false, $context);

    if ($response_body === false) {
        return new WP_Error('http_error', 'Failed to connect to backend server');
    }

    // Parse Response Headers for HTTP status code
    $status_line = $http_response_header[0];
    preg_match('{HTTP\/\S*\s(\d+)}', $status_line, $match);
    $http_code = intval($match[1]);

    return [
        'body' => $response_body,
        'response' => [
            'code' => $http_code
        ]
    ];
}

function wp_remote_retrieve_response_code($response) {
    return $response['response']['code'];
}

function wp_remote_retrieve_body($response) {
    return $response['body'];
}


// --- ORIGINAL USER CLASS START ---
class NexusPress_API_Client {

    // Pointing to local Python engine backend server for testing
    private $api_url = 'http://127.0.0.1:8000/api/v1/generate-ai';

    /**
     * Sends post metadata to Railway backend and retrieves AI SEO output.
     */
    public function generate_seo_data($post_title, $post_excerpt) {
        $license_key = get_option('nexuspress_license_key', '');

        if (empty($license_key)) {
            return new WP_Error('missing_key', __('Please enter your NexusPress license key in settings.', 'nexuspress'));
        }

        $body = wp_json_encode(array(
            'title'   => sanitize_text_field($post_title),
            'content' => sanitize_textarea_field($post_excerpt)
        ));

        $args = array(
            'body'        => $body,
            'headers'     => array(
                'Content-Type'  => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($license_key),
            ),
            'timeout'     => 15,
            'data_format' => 'body',
        );

        $response = wp_remote_post($this->api_url, $args);

        if (is_wp_error($response)) {
            return $response;
        }

        $response_code = wp_remote_retrieve_response_code($response);
        $response_body = wp_remote_retrieve_body($response);

        if ($response_code !== 200) {
            $data = json_decode($response_body, true);
            $message = isset($data['error']) ? $data['error'] : __('Server error encountered.', 'nexuspress');
            return new WP_Error('api_error', $message);
        }

        return json_decode($response_body, true);
    }
}
// --- ORIGINAL USER CLASS END ---

// Execution Test Runner
$client = new NexusPress_API_Client();
echo "Connecting to local NexusPress AI python engine backend...\n";
$res = $client->generate_seo_data(
    "Automating Digital Content with AI",
    "Discover how workflow execution pipelines optimize content generation strategies."
);

if (is_wp_error($res)) {
    echo "ERROR [{$res->code}]: {$res->message}\n";
    exit(1);
} else {
    echo "SUCCESS! Received SEO Response payload:\n";
    echo json_encode($res, JSON_PRETTY_PRINT) . "\n";
}
