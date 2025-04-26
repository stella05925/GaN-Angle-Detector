image = imread('TEM/DF-17500x-220-20obj-cGaN-01.tif');
if size(image, 3) > 1
    image_gray = rgb2gray(image);
else
    image_gray = image;
end
sigma = 2.5;
gaus_kernel = fspecial('gaussian', 17, sigma);
image_filt = imfilter(image, gaus_kernel);

image_fou = fftshift(abs(fft2(image_filt))) / 50;
%imshow(image_fou);

% higher high threshold
edges = edge(image_filt, 'canny', [0.1, 0.2]);

%imshow(edges);

se = strel('line', 5, 90);
edges_cleaned = imclose(edges, se);
edges_cleaned = bwareaopen(edges_cleaned, 20); % Remove small objects
figure; imshow(edges_cleaned); title('Cleaned Edges');

% Apply Hough transform with targeted angle ranges
[H1, T1, R1] = hough(edges_cleaned, 'Theta', -65:-25);
[H2, T2, R2] = hough(edges_cleaned, 'Theta', 25:65);

% Find the strongest peak in each angle range
P1 = houghpeaks(H1, 1, 'threshold', 0.2*max(H1(:)));
P2 = houghpeaks(H2, 1, 'threshold', 0.2*max(H2(:)));

% Extract lines
lines1 = houghlines(edges_cleaned, T1, R1, P1, 'FillGap', 15, 'MinLength', 20);
lines2 = houghlines(edges_cleaned, T2, R2, P2, 'FillGap', 15, 'MinLength', 20);

% Combine lines from both angle ranges
% After Hough line detection
lines = [lines1, lines2];

% Display all detected line segments for visualization
% After your existing line detection but BEFORE the angle-based sorting
% Display all lines with their orientation angles for debugging
figure; imshow(image_gray); hold on;
title('All Detected Lines with Angles');

for k = 1:length(lines)
    line = lines(k);
    x1 = line.point1(1); y1 = line.point1(2);
    x2 = line.point2(1); y2 = line.point2(2);
    
    % Calculate angle
    angle = atan2(y2-y1, x2-x1) * 180/pi;
    
    % Plot with color based on angle
    if angle > 0
        plot([x1, x2], [y1, y2], 'LineWidth', 2, 'Color', 'red');
    else
        plot([x1, x2], [y1, y2], 'LineWidth', 2, 'Color', 'blue');
    end
    
    % Show the angle value near the line
    text((x1+x2)/2, (y1+y2)/2, [num2str(angle, '%.1f') '°'], 'Color', 'white', 'FontSize', 8, 'BackgroundColor', 'black');
end

% Modify your angle sorting to use a broader range for the right side
% Replace your current angle sorting with this:
left_side_lines = [];
right_side_lines = [];

for k = 1:length(lines)
    line = lines(k);
    x1 = line.point1(1); y1 = line.point1(2);
    x2 = line.point2(1); y2 = line.point2(2);
    
    % Calculate angle to determine if it's left or right side
    angle = atan2(y2-y1, x2-x1) * 180/pi;
    
    % Use angle ranges specific to your crystal
    fprintf('Line %d: angle = %.2f degrees\n', k, angle);
    
    if angle > 90  % Higher angle group (around 127 degrees)
        left_side_lines = [left_side_lines; line];
        fprintf('  -> Assigned to LEFT side\n');
    else  % Lower angle group (around 57-58 degrees)
        right_side_lines = [right_side_lines; line];
        fprintf('  -> Assigned to RIGHT side\n');
    end
end

% Print how many lines were assigned to each side
fprintf('Number of left side lines: %d\n', length(left_side_lines));
fprintf('Number of right side lines: %d\n', length(right_side_lines));

% Create a new figure for the consolidated lines
figure; imshow(image_gray); hold on;
title('Consolidated Lines');

% For left side - handle multiple lines via linear regression
left_points = [];
if ~isempty(left_side_lines)
    for i = 1:length(left_side_lines)
        left_points = [left_points; left_side_lines(i).point1; left_side_lines(i).point2];
    end
    
    % Linear regression for left points
    x = left_points(:, 1);
    y = left_points(:, 2);
    p_left = polyfit(x, y, 1);
    
    % Get endpoints for drawing
    x_min = min(x);
    x_max = max(x);
    left_x1 = x_min; left_y1 = p_left(1) * x_min + p_left(2);
    left_x2 = x_max; left_y2 = p_left(1) * x_max + p_left(2);
    
    % Draw consolidated left line
    plot([left_x1, left_x2], [left_y1, left_y2], 'LineWidth', 3, 'Color', 'blue');
    text(left_x1, left_y1, 'Left Side', 'Color', 'blue', 'FontSize', 12);
end

% For right side - use the original line if only one was detected
if ~isempty(right_side_lines)
    if length(right_side_lines) == 1
        % Use the single detected line directly
        line = right_side_lines(1);
        right_x1 = line.point1(1); right_y1 = line.point1(2);
        right_x2 = line.point2(1); right_y2 = line.point2(2);
    else
        % Multiple lines - use linear regression as with left side
        right_points = [];
        for i = 1:length(right_side_lines)
            right_points = [right_points; right_side_lines(i).point1; right_side_lines(i).point2];
        end
        
        x = right_points(:, 1);
        y = right_points(:, 2);
        p_right = polyfit(x, y, 1);
        
        x_min = min(x);
        x_max = max(x);
        right_x1 = x_min; right_y1 = p_right(1) * x_min + p_right(2);
        right_x2 = x_max; right_y2 = p_right(1) * x_max + p_right(2);
    end
    
    % Draw consolidated right line
    plot([right_x1, right_x2], [right_y1, right_y2], 'LineWidth', 3, 'Color', 'red');
    text(right_x2, right_y2, 'Right Side', 'Color', 'red', 'FontSize', 12);
end

% Calculate angle between the two lines if both sides are detected
if exist('left_x1', 'var') && exist('right_x1', 'var')
    % Calculate direction vectors - pay special attention to vector direction
    left_vector = [left_x2-left_x1, left_y2-left_y1];
    right_vector = [right_x2-right_x1, right_y2-right_y1];
    
    % Print vectors for debugging
    fprintf('Left vector: [%.2f, %.2f]\n', left_vector(1), left_vector(2));
    fprintf('Right vector: [%.2f, %.2f]\n', right_vector(1), right_vector(2));
    
    % Normalize
    left_norm = norm(left_vector);
    right_norm = norm(right_vector);
    
    % Check for zero-length vectors
    if left_norm < 1e-6 || right_norm < 1e-6
        warning('One of the vectors has zero length!');
        left_vector_norm = left_vector / max(left_norm, 1e-6);
        right_vector_norm = right_vector / max(right_norm, 1e-6);
    else
        left_vector_norm = left_vector / left_norm;
        right_vector_norm = right_vector / right_norm;
    end
    
    % Calculate dot product
    dot_product = dot(left_vector_norm, right_vector_norm);
    fprintf('Dot product: %.6f\n', dot_product);
    
    % Ensure dot product is in valid range for acos
    dot_product = min(1, max(-1, dot_product));
    
    % Calculate angle in degrees
    angle_between = acosd(dot_product);
    fprintf('Raw angle: %.2f degrees\n', angle_between);
    
    % If angle is obtuse, take its supplement
    if angle_between > 90
        angle_between = 180 - angle_between;
    end
    
    fprintf('Final angle: %.2f degrees\n', angle_between);
    
    % Find midpoint for text placement
    mid_x = mean([left_x1, left_x2, right_x1, right_x2]);
    mid_y = mean([left_y1, left_y2, right_y1, right_y2]);
    
    % Display angle
    text(mid_x, mid_y, [num2str(angle_between, '%.2f') '°'], ...
         'Color', 'green', 'FontSize', 14, 'FontWeight', 'bold', 'BackgroundColor', 'white');
    
    title(['Crystal Angle: ' num2str(angle_between, '%.2f') '°']);
end