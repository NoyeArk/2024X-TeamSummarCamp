dataset_path="D:/Code/Paper-code/DINO/Coco"
dataset_path="D:/Code/Paper-code/DINO/ExDark/data"

python main.py \
	--output_dir logs/DINO/R50-MS4 -c config/AFT/aft_simple.py --coco_path $dataset_path \
	--dataset_file=coco --options dn_scalar=100 embed_init_tgt=TRUE \
	dn_label_coef=1.0 dn_bbox_coef=1.0 use_ema=False \
	dn_box_noise_scale=1.0
