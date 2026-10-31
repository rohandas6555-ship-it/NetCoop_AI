def build_recommendations(cause, evidence):
    mapping = {
      'Link congestion': ['Inspect uplink utilization and identify top bandwidth consumers.', 'Check QoS policies and queue-drop counters.', 'Consider load balancing or increasing capacity only if sustained saturation is confirmed.'],
      'Weak Wi-Fi signal': ['Inspect AP placement, transmit power and channel overlap.', 'Check client distance, obstacles and interference.', 'Validate coverage with a site survey before changing radio settings.'],
      'Ethernet/interface fault': ['Inspect cable, transceiver and switch port health.', 'Review interface CRC/errors and link-flap logs.', 'Test with a known-good cable/port and verify speed/duplex negotiation.'],
      'DNS/DHCP service failure': ['Verify DNS/DHCP server reachability and service health.', 'Check DNS query logs, DHCP scope utilization and lease failures.', 'Validate client DNS/DHCP configuration and upstream routing.'],
      'No significant fault detected': ['Continue monitoring and compare against a known-good baseline.', 'Collect longer-duration telemetry if users continue to report issues.'],
      'No fault detected in available telemetry': ['Collect missing telemetry domains before declaring the network healthy.', 'Gather DNS/DHCP, Wi-Fi signal/retransmission, and interface health metrics as applicable.', 'Compare a longer time window against a known-good baseline.']
    }
    actions = next((items for key, items in mapping.items() if cause.startswith(key)), None)
    if not actions:
        actions = ['Collect additional telemetry (interface counters, routing, DNS/DHCP and Wi-Fi metrics).', 'Correlate the incident with device logs and recent configuration changes.', 'Escalate for manual network-operator review if impact persists.']
    from app.llm.groq_service import analyze_with_groq
    llm = analyze_with_groq('Recommendation Agent',
        'Review actions for relevance. Add cautious diagnostic checks only; do not propose unverified disruptive changes.',
        {'suspected_root_cause': cause, 'evidence': evidence, 'rule_based_actions': actions},
        ['summary', 'additional_checks', 'operator_cautions'])
    return {'agent':'recommendation_agent','status':'ready',
            'findings':[f'Recommendations prepared for: {cause}'],
            'evidence':evidence,'recommended_actions':actions,'llm_analysis':llm}
