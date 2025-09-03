
matrix_width = 159;
matrix_height = 159;
grid_depth = 14.2;

font_size = 8;
small_letter_font_offset = 2;
big_letter_font_offset = -2;

grid_wall_thickness = 0.5;
cell_size = matrix_width / 16.0;
hole_size = cell_size - (2.0*grid_wall_thickness);

number_cells = 16;


top_width = 169.22;
top_height = 169.22;
top_depth = 7;  // 22 for full, 7 for short
top_wall_thickness = 2;
top_face_thickness = 2;
top_face_indent = 1;

letter_size = cell_size; //top_width / 16.0;
bottom_wall_thickness = (top_width - matrix_width) / 2;

inset_width = 10;
inset_depth = 1;

// The grid

*difference() {
    cube([matrix_width, matrix_height, grid_depth]);
    
    for (j=[0: 1: number_cells-1]) {
        for (i=[0: 1: number_cells-1]) {
            translate(v=[
                (cell_size * i) + grid_wall_thickness, 
                (cell_size * j) + grid_wall_thickness, 
            0]) {
                cube([
                    hole_size, 
                    hole_size, 
                    40
                ]);
            };
        }
    }
}




old_face = [
"■■■■■■■■■■■■■■■■",
"■@@@@@@@@@@@@@@■",
"■@@@@@@@@@@@@@@■",
"■@SITLISYAMAPM@■",
"■@QUARTERYACDC@■",
"■@RTWENTYYFIVE@■",
"■@HALFSYTENFTO@■",
"■@PASTERUYNINE@■",
"■@ONESIXYTHREE@■",
"■@FOURFIVEYTWO@■",
"■@EIGHTYELEVEN@■",
"■@SEVENYTWELVE@■",
"■@TENSYOCLOCKX@■",
"■@@@@@@@@@@@@@@■",
"■@@@@@@@@@@@@@@■",
"■■■■■■■■■■■■■■■■",
];

face = [
"■■■■■■■■■■■■■■■■",
"■@@@@@@@@@@@@@@■",
"■@@@@@@@@@@@@@@■",
"■@JIT0IS1AMAPM@■",
"■@QUARTER2ZERO@■",
"■@RTWENTYYFIVE@■",
"■@HALF34TEN5TO@■",
"■@PASTEDOTNINE@■",
"■@ONESIX6THREE@■",
"■@FOURFIVE7TWO@■",
"■@EIGHT8ELEVEN@■",
"■@SEVENZTWELVE@■",
"■@TEN9MOCLOCKB@■",
"■@@@@@@@@@@@@@@■",
"■@@@@@@@@@@@@@@■",
"■■■■■■■■■■■■■■■■",
];


/*
face = [
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
"■■■■■■■■■■■■■■■■",
];
*/
y_offset = 2;


// The letters and the box
module square_perimeter(size, thickness) {
    difference() {
        square(size = size); // Outer square
        translate([thickness, thickness, 0]) {
            square(size = size - [2 * thickness, 2 * thickness]); // Inner square
        };
    }
}


difference() {
    cube([top_width, top_height, top_depth]);
    {
        translate([top_wall_thickness, top_wall_thickness, 0]) {
            cube([top_width-2*top_wall_thickness, top_height-2*     top_wall_thickness, top_depth-top_face_thickness]);
        };

        
        for (j=[0: 1: number_cells-1]) {
            for (i=[0: 1: number_cells-1]) {
                letter = face[j][i];
                x = i;
                y = number_cells - j - 1;
                offset = (letter == "I" || letter == "■" || letter == "J" )? small_letter_font_offset:  (letter == "M" || letter == "W")? big_letter_font_offset: 0;
                if (letter != "@") {
                    translate(v=[
                        (letter_size * x) + bottom_wall_thickness + offset, 
                        (letter_size * y) + bottom_wall_thickness + y_offset, 
                    0]) {
                        font_name = (letter == "■") ? "" : "Saira Stencil One:style=Regular";
                        linear_extrude(40) {
                            text(letter, font_size,
                                font=font_name
                            );
                        };
                    };
                };
            };
        };
        
        // Inset line - not needed any more
        
        /*
        
        translate([inset_width, inset_width, top_depth - inset_depth]) {
            linear_extrude(10) {
                square_perimeter(size=[
                    (top_width - (2*inset_width)), (top_width - (2*inset_width))], thickness=inset_depth
                );
            };
        };
        */
        
    };    

    
};

