# Data Dictionary

## Source Tables

### raw_users

- `user_id`: Unique user identifier.
- `first_seen_date`: Date the user first entered the funnel.
- `signup_date`: Date the user signed up, if applicable.
- `activation_date`: Date the user activated, if applicable.
- `acquisition_channel`: User acquisition source.
- `country`: User country.
- `device_type`: Primary device type.

### raw_sessions

- `session_id`: Unique session identifier.
- `user_id`: User linked to the session.
- `session_start`: Session start timestamp.
- `session_end`: Session end timestamp.
- `traffic_source`: Session traffic source.
- `landing_page`: First page in the session.
- `device_type`: Session device type.

### raw_events

- `event_id`: Unique event identifier.
- `session_id`: Session linked to the event.
- `user_id`: User linked to the event.
- `event_time`: Event timestamp.
- `event_name`: Product event name.
- `page_name`: Page associated with the event.

### raw_signups

- `signup_id`: Unique signup identifier.
- `user_id`: User linked to the signup.
- `signup_date`: Signup date.
- `signup_method`: Signup method.
- `signup_status`: Signup completion status.

### raw_conversions

- `conversion_id`: Unique conversion identifier.
- `user_id`: User linked to the conversion.
- `conversion_date`: Conversion date.
- `conversion_type`: Conversion category.
- `revenue`: Revenue generated.
- `plan_name`: Purchased plan.

## Feature Mart

### mart_user_features

- `did_signup`: Binary flag for signup.
- `did_activate`: Binary flag for activation.
- `did_convert`: Binary modeling target.
- `session_count`: Number of user sessions.
- `total_session_minutes`: Total session duration.
- `avg_session_minutes`: Average session duration.
- `unique_landing_pages`: Number of distinct landing pages.
- `event_count`: Total events.
- `pricing_views`: Count of pricing page events.
- `signup_started_events`: Count of signup-start events.
- `signup_completed_events`: Count of signup-complete events.
- `activation_events`: Count of activation events.
- `purchase_events`: Count of purchase events.
- `days_to_signup`: Days from first seen to signup, or -1 if not signed up.
- `days_to_activation`: Days from signup to activation, or -1 if not activated.

## Model Output

### mart_conversion_scores

- `user_id`: User identifier.
- `conversion_probability`: Predicted probability of conversion.
- `risk_segment`: Low, medium, or high propensity segment.
- `did_convert`: Actual conversion flag.
- `total_revenue`: Actual user revenue.
