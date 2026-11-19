<?php
/*
Plugin Name: Backlink Manager API
Description: Custom REST API endpoints for Backlink Manager Pro
Version: 1.0
Author: WebAdHere
Author URI: https://webadhere.com
*/

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Register REST API endpoints
add_action('rest_api_init', function () {
    // Authentication endpoint
    register_rest_route('backlink-manager/v1', '/auth', array(
        'methods' => 'POST',
        'callback' => 'bm_authenticate',
        'permission_callback' => '__return_true'
    ));

    // Create post endpoint
    register_rest_route('backlink-manager/v1', '/posts', array(
        'methods' => 'POST',
        'callback' => 'bm_create_post',
        'permission_callback' => 'bm_check_auth'
    ));
    
    // Upload image endpoint
    register_rest_route('backlink-manager/v1', '/upload-image', array(
        'methods' => 'POST',
        'callback' => 'bm_upload_image',
        'permission_callback' => 'bm_check_auth'
    ));
});

// Authentication function
function bm_authenticate($request) {
    $username = $request->get_param('username');
    $password = $request->get_param('password');

    $user = wp_authenticate($username, $password);

    if (is_wp_error($user)) {
        return new WP_Error(
            'auth_failed',
            'Authentication failed',
            array('status' => 401)
        );
    }

    if (!user_can($user->ID, 'edit_posts') || !user_can($user->ID, 'publish_posts')) {
        return new WP_Error(
            'insufficient_permissions',
            'User must have content editing permissions',
            array('status' => 403)
        );
    }

    $token = array(
        'user' => $user->ID,
        'exp' => time() + (7 * DAY_IN_SECONDS)
    );

    return array(
        'token' => jwt_encode_token($token),
        'user_id' => $user->ID,
        'user_login' => $user->user_login
    );
}

// JWT token encoding
function jwt_encode_token($payload) {
    $key = wp_salt('auth');
    $header = array(
        'typ' => 'JWT',
        'alg' => 'HS256'
    );

    $header_encoded = base64url_encode(json_encode($header));
    $payload_encoded = base64url_encode(json_encode($payload));

    $signature_input = "$header_encoded.$payload_encoded";
    $signature = hash_hmac('sha256', $signature_input, $key, true);
    $signature_encoded = base64url_encode($signature);

    return "$header_encoded.$payload_encoded.$signature_encoded";
}

// Base64URL encoding
function base64url_encode($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

// Check authentication
function bm_check_auth($request) {
    $auth_header = $request->get_header('Authorization');
    if (!$auth_header || strpos($auth_header, 'Bearer ') !== 0) {
        return false;
    }

    $token = substr($auth_header, 7);
    $decoded = jwt_decode_token($token);

    if (!$decoded || !isset($decoded['user']) || time() > $decoded['exp']) {
        return false;
    }

    return true;
}

// JWT token decoding
function jwt_decode_token($token) {
    $key = wp_salt('auth');
    $parts = explode('.', $token);

    if (count($parts) !== 3) {
        return false;
    }

    $signature_input = "{$parts[0]}.{$parts[1]}";
    $signature = base64url_decode($parts[2]);
    $expected_signature = hash_hmac('sha256', $signature_input, $key, true);

    if (!hash_equals($signature, $expected_signature)) {
        return false;
    }

    return json_decode(base64url_decode($parts[1]), true);
}

// Base64URL decoding
function base64url_decode($data) {
    return base64_decode(strtr($data, '-_', '+/') . str_repeat('=', 3 - (3 + strlen($data)) % 4));
}

// Upload image function
function bm_upload_image($request) {
    // Get the image data from the request
    $image_data = $request->get_param('image_data');
    $image_name = $request->get_param('image_name');
    
    if (empty($image_data) || empty($image_name)) {
        return new WP_Error(
            'missing_fields',
            'Image data and name are required',
            array('status' => 400)
        );
    }
    
    // Decode the base64 image data
    $decoded_image = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $image_data));
    
    if (!$decoded_image) {
        return new WP_Error(
            'invalid_image',
            'Invalid image data',
            array('status' => 400)
        );
    }
    
    // Get WordPress upload directory
    $upload_dir = wp_upload_dir();
    
    // Create a unique filename
    $filename = wp_unique_filename($upload_dir['path'], $image_name);
    $filepath = $upload_dir['path'] . '/' . $filename;
    
    // Save the image file
    file_put_contents($filepath, $decoded_image);
    
    // Prepare attachment data
    $attachment = array(
        'post_mime_type' => mime_content_type($filepath),
        'post_title' => sanitize_file_name($filename),
        'post_content' => '',
        'post_status' => 'inherit'
    );
    
    // Insert attachment into the database
    $attach_id = wp_insert_attachment($attachment, $filepath);
    
    if (is_wp_error($attach_id)) {
        return new WP_Error(
            'attachment_failed',
            'Failed to create attachment',
            array('status' => 500)
        );
    }
    
    // Generate metadata for the attachment
    require_once(ABSPATH . 'wp-admin/includes/image.php');
    $attach_data = wp_generate_attachment_metadata($attach_id, $filepath);
    wp_update_attachment_metadata($attach_id, $attach_data);
    
    return array(
        'id' => $attach_id,
        'url' => wp_get_attachment_url($attach_id),
        'title' => $attachment['post_title']
    );
}

// Create post function
function bm_create_post($request) {
    $title = sanitize_text_field($request->get_param('title'));
    $content = wp_kses_post($request->get_param('content'));
    $status = $request->get_param('status');
    $featured_image_id = $request->get_param('featured_image_id');

    if (empty($title) || empty($content)) {
        return new WP_Error(
            'missing_fields',
            'Title and content are required',
            array('status' => 400)
        );
    }

    $post_data = array(
        'post_title' => $title,
        'post_content' => $content,
        'post_status' => $status,
        'post_author' => get_current_user_id(),
        'post_type' => 'post'
    );

    $post_id = wp_insert_post($post_data);

    if (is_wp_error($post_id)) {
        return new WP_Error(
            'post_creation_failed',
            'Failed to create post',
            array('status' => 500)
        );
    }
    
    // Set featured image if provided
    if (!empty($featured_image_id) && is_numeric($featured_image_id)) {
        set_post_thumbnail($post_id, $featured_image_id);
    }

    return array(
        'id' => $post_id,
        'title' => $title,
        'status' => $status,
        'featured_image_id' => $featured_image_id
    );
}