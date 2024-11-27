String analyzeFeasibility(const dataPacket& input) {
    // Thresholds and conditions for analysis
    float maxWindSpeed = 10.0; // Maximum wind speed in m/s
    String unsafeDirections[] = {"selatan", "barat daya"}; // Unsafe wind directions
    bool isUnsafeDirection = false;

    // Check wind direction safety
    for (String dir : unsafeDirections) {
        if (input.direction.equals(dir)) {
            isUnsafeDirection = true;
            break;
        }
    }

    // Analyze feasibility
    if (input.shoreStatus == "PASANG") {
        return "Tidak aman berlayar: Air sedang pasang.";
    } else if (input.speed > maxWindSpeed) {
        return "Tidak aman berlayar: Kecepatan angin terlalu tinggi.";
    } else if (isUnsafeDirection) {
        return "Tidak aman berlayar: Arah angin tidak mendukung.";
    } else {
        return "Aman untuk berlayar.";
    }
}
