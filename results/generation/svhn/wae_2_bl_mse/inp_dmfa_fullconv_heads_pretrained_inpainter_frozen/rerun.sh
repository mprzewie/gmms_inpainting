# 2021-03-01 14:16:30.015241
python train_wae.py --experiment_name=wae_2_bl_mse/inp_dmfa_fullconv_heads_pretrained_inpainter_frozen --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/mse_for_10_epochs/ --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --wae_bl 2 --wae_recon_loss mse
